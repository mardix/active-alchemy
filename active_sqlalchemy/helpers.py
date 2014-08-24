# -*- coding: utf-8 -*-
import threading
import json
import datetime
import inflection
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import scoped_session, sessionmaker, Query
from .paginator import Paginator


def _create_scoped_session(db, query_cls):
    session = sessionmaker(autoflush=True, autocommit=False,
                           bind=db.engine, query_cls=query_cls)
    return scoped_session(session)


def _tablemaker(db):
    def make_sa_table(*args, **kwargs):
        if len(args) > 1 and isinstance(args[1], db.Column):
            args = (args[0], db.metadata) + args[1:]
        kwargs.setdefault('bind_key', None)
        info = kwargs.pop('info', None) or {}
        info.setdefault('bind_key', None)
        kwargs['info'] = info
        return sqlalchemy.Table(*args, **kwargs)

    return make_sa_table


def _include_sqlalchemy(db):
    for module in sqlalchemy, sqlalchemy.orm:
        for key in module.__all__:
            if not hasattr(db, key):
                setattr(db, key, getattr(module, key))
    db.Table = _tablemaker(db)
    db.event = sqlalchemy.event


class BaseQuery(Query):

    def get_or_error(self, uid, error):
        """Like :meth:`get` but raises an error if not found instead of
        returning `None`.
        """
        rv = self.get(uid)
        if rv is None:
            if isinstance(error, Exception):
                raise error
            return error()
        return rv

    def first_or_error(self, error):
        """Like :meth:`first` but raises an error if not found instead of
        returning `None`.
        """
        rv = self.first()
        if rv is None:
            if isinstance(error, Exception):
                raise error
            return error()
        return rv

    def paginate(self, **kwargs):
        """Paginate this results.
        Returns an :class:`Pagination` object.
        """
        return Paginator(self, **kwargs)


class ModelTableNameDescriptor(object):
    """
    Create the table name if it doesn't exist.
    """
    def __get__(self, obj, type):
        tablename = type.__dict__.get('__tablename__')
        if not tablename:
            tablename = inflection.underscore(type.__name__)
            setattr(type, '__tablename__', tablename)
        return tablename


class EngineConnector(object):

    def __init__(self, sa_obj):
        self._sa_obj = sa_obj
        self._engine = None
        self._connected_for = None
        self._lock = threading.Lock()

    def get_engine(self):
        with self._lock:
            uri = self._sa_obj.uri
            info = self._sa_obj.info
            options = self._sa_obj.options
            echo = options.get('echo')
            if (uri, echo) == self._connected_for:
                return self._engine
            self._engine = engine = sqlalchemy.create_engine(info, **options)
            self._connected_for = (uri, echo)
            return engine

class IDMixin(object):
    """
    A mixin to add an id
    """
    id = Column(Integer, primary_key=True)

class Model(object):
    """
    Baseclass for custom user models.
    """

    __tablename__ = ModelTableNameDescriptor()

    def __iter__(self):
        """Returns an iterable that supports .next()
        so we can do dict(sa_instance).
        """
        print "I'm in"
        for k in self.__dict__.keys():
            if not k.startswith('_'):
                yield (k, getattr(self, k))

    def __repr__(self):
        return '<%s>' % self.__class__.__name__



class ActiveModel(IDMixin, Model):
    """
    Model create
    """
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime)

    @classmethod
    def get(cls, id, exclude_deleted=True):
        """
        Select entry by id
        :param id: The id of the entry
        :param exclude_deleted: It should not query deleted record. Set to false to get all
        """
        query = cls.query(cls).filter(cls.id == id)
        if exclude_deleted:
            query = cls.exclude_deleted(query)
        return query.first()

    @classmethod
    def all(cls, *args, **kwargs):
        """
        :returns query:
        """
        _exclude_deleted = True
        if "exclude_deleted" in kwargs:
            _exclude_deleted = kwargs["exclude_deleted"]
            del kwargs["exclude_deleted"]

        if not args:
            query = cls.query(cls)
        else:
            query = cls.query(*args)
        if _exclude_deleted:
            query = cls.exclude_deleted(query)
        return query

    @classmethod
    def insert(cls, **kwargs):
        """
        To insert new
        """
        record = cls(**kwargs).save()
        return record

    def update(self, **kwargs):
        """
        Update an entry
        """
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.save()
        return self

    def delete(self, delete=True, hard_delete=False):
        """
        Soft delete a record
        :param delete: Bool - To soft-delete/soft-undelete a record
        :param hard_delete: Bool - If true it will completely delete the record
        """
        # Hard delete
        if hard_delete:
            self.db.session.delete(self)
            return self.db.commit()
        else:
            data = {
                "is_deleted": delete,
                "deleted_at": func.now() if delete else None
            }
            self.update(**data)
        return self


    @classmethod
    def exclude_deleted(cls, query):
        """
        Add filter to exclude deleted items
        """
        query = query.filter(cls.is_deleted != True)
        return query

    def save(self):
        """
        Shortcut to add and save
        """
        self.db.add(self)
        self.db.commit()
        return self

    def rollback(self):
        self.db.rollback(self)
        return self

    def to_dict(self):
        """
        Return an entity as dict
        :returns dict:
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_json(self):
        """
        Convert the entity to JSON
        :returns str:
        """
        data = {}
        for k, v in self.to_dict().items():
            if isinstance(v, datetime.datetime):
                v = v.isoformat()
            data[k] = v
        return json.dumps(data)

