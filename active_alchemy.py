# -*- coding: utf-8 -*-
"""
==================
Active-Alchemy
==================

A framework agnostic wrapper for SQLAlchemy that makes it really easy
to use by implementing a simple active record like api, while it still uses the db.session underneath

:copyright: © 2014 by `Mardix`.
:license: MIT, see LICENSE for more details.

"""

NAME = "Active-Alchemy"

# ------------------------------------------------------------------------------

import threading
import json
import datetime
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import scoped_session, sessionmaker, Query
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData
from paginator import Paginator
import inflection

DEFAULT_PER_PAGE = 10

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
        Returns an :class:`Paginator` object.
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


class BaseModel(object):
    """
    Baseclass for custom user models.
    """

    __tablename__ = ModelTableNameDescriptor()

    def __iter__(self):
        """Returns an iterable that supports .next()
        so we can do dict(sa_instance).
        """
        for k in self.__dict__.keys():
            if not k.startswith('_'):
                yield (k, getattr(self, k))

    def __repr__(self):
        return '<%s>' % self.__class__.__name__

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

    @classmethod
    def get(cls, id):
        """
        Select entry by id
        :param id: The id of the entry
        """
        return cls.query(cls).filter(cls.id == id).first()

    @classmethod
    def create(cls, **kwargs):
        """
        To create a new record
        :returns object: The new record
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

    @classmethod
    def all(cls, *args):
        """
        :returns query:
        """
        if not args:
            query = cls.query(cls)
        else:
            query = cls.query(*args)
        return query

    def save(self):
        """
        Shortcut to add and save + rollback
        """
        try:
            self.db.add(self)
            self.db.commit()
            return self
        except Exception as e:
            self.db.rollback()
            raise

    def delete(self, delete=True, hard_delete=False):
        """
        Soft delete a record 
        :param delete: Bool - To soft-delete/soft-undelete a record
        :param hard_delete: Bool - *** Not applicable under BaseModel 
                            
        """
        try:
            self.db.session.delete(self)
            return self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise


class Model(IDMixin, BaseModel):
    """
    Model create
    """
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime, default=None)

    @classmethod
    def all(cls, *args, **kwargs):
        """
        :returns query:

        :**kwargs:
            - include_deleted bool: True To filter in deleted records.
                                    By default it is set to False
        """
        if not args:
            query = cls.query(cls)
        else:
            query = cls.query(*args)

        if "include_deleted" not in kwargs or kwargs["include_deleted"] is False:
            query = query.filter(cls.is_deleted != True)

        return query

    @classmethod
    def get(cls, id, include_deleted=False):
        """
        Select entry by id
        :param id: The id of the entry
        :param include_deleted: It should not query deleted record. Set to True to get all
        """
        return cls.all(include_deleted=include_deleted)\
                  .filter(cls.id == id)\
                  .first()

    def delete(self, delete=True, hard_delete=False):
        """
        Soft delete a record
        :param delete: Bool - To soft-delete/soft-undelete a record
        :param hard_delete: Bool - If true it will completely delete the record
        """
        # Hard delete
        if hard_delete:
            try:
                self.db.session.delete(self)
                return self.db.commit()
            except:
                self.db.rollback()
                raise
        else:
            data = {
                "is_deleted": delete,
                "deleted_at": func.now() if delete else None
            }
            self.update(**data)
        return self


class SQLAlchemy(object):
    """This class is used to instantiate a SQLAlchemy connection to
    a database.

        db = SQLAlchemy(_uri_to_database_)

    The class also provides access to all the SQLAlchemy
    functions from the :mod:`sqlalchemy` and :mod:`sqlalchemy.orm` modules.
    So you can declare models like this::

        class User(db.Model):
            login = db.Column(db.String(80), unique=True)
            passw_hash = db.Column(db.String(80))

    In a web application you need to call `db.session.remove()`
    after each response, and `db.session.rollback()` if an error occurs.
    If your application object has a `after_request` and `on_exception
    decorators, just pass that object at creation::

        app = Flask(__name__)
        db = SQLAlchemy('sqlite://', app=app)

    or later::

        db = SQLAlchemy()

        app = Flask(__name__)
        db.init_app(app)

    .. admonition:: Check types carefully

       Don't perform type or `isinstance` checks against `db.Table`, which
       emulates `Table` behavior but is not a class. `db.Table` exposes the
       `Table` interface, but is a function which allows omission of metadata.

    """

    def __init__(self, uri='sqlite://',
                 app=None,
                 echo=False,
                 pool_size=None,
                 pool_timeout=None,
                 pool_recycle=None,
                 convert_unicode=True,
                 query_cls=BaseQuery):

        self.uri = uri
        self.info = make_url(uri)
        self.options = self._cleanup_options(
            echo=echo,
            pool_size=pool_size,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            convert_unicode=convert_unicode,
        )

        self.connector = None
        self._engine_lock = threading.Lock()
        self.session = _create_scoped_session(self, query_cls=query_cls)

        self.Model = declarative_base(cls=Model, name='Model')
        self.BaseModel = declarative_base(cls=BaseModel, name='BaseModel')

        self.Model.db, self.BaseModel.db = self, self
        self.Model.query, self.BaseModel.query = self.session.query, self.session.query

        if app is not None:
            self.init_app(app)

        _include_sqlalchemy(self)

    def _cleanup_options(self, **kwargs):
        options = dict([
            (key, val)
            for key, val in kwargs.items()
            if val is not None
        ])
        return self._apply_driver_hacks(options)

    def _apply_driver_hacks(self, options):
        if "mysql" in self.info.drivername:
            self.info.query.setdefault('charset', 'utf8')
            options.setdefault('pool_size', 10)
            options.setdefault('pool_recycle', 7200)
        elif self.info.drivername == 'sqlite':
            no_pool = options.get('pool_size') == 0
            memory_based = self.info.database in (None, '', ':memory:')
            if memory_based and no_pool:
                raise ValueError(
                    'SQLite in-memory database with an empty queue'
                    ' (pool_size = 0) is not possible due to data loss.'
                )
        return options

    def init_app(self, app):
        """This callback can be used to initialize an application for the
        use with this database setup. In a web application or a multithreaded
        environment, never use a database without initialize it first,
        or connections will leak.
        """
        if not hasattr(app, 'databases'):
            app.databases = []
        if isinstance(app.databases, list):
            if self in app.databases:
                return
            app.databases.append(self)

        def shutdown(response=None):
            self.session.remove()
            return response

        def rollback(error=None):
            try:
                self.session.rollback()
            except Exception:
                pass

        self.set_flask_hooks(app, shutdown, rollback)

    def set_flask_hooks(self, app, shutdown, rollback):
        if hasattr(app, 'after_request'):
            app.after_request(shutdown)
        if hasattr(app, 'on_exception'):
            app.on_exception(rollback)

    @property
    def engine(self):
        """Gives access to the engine. """
        with self._engine_lock:
            connector = self.connector
            if connector is None:
                connector = EngineConnector(self)
                self.connector = connector
            return connector.get_engine()

    @property
    def metadata(self):
        """Proxy for Model.metadata"""
        return self.Model.metadata

    @property
    def query(self):
        """Proxy for session.query"""
        return self.session.query

    def add(self, *args, **kwargs):
        """Proxy for session.add"""
        return self.session.add(*args, **kwargs)

    def flush(self, *args, **kwargs):
        """Proxy for session.flush"""
        return self.session.flush(*args, **kwargs)

    def commit(self):
        """Proxy for session.commit"""
        return self.session.commit()

    def rollback(self):
        """Proxy for session.rollback"""
        return self.session.rollback()

    def create_all(self):
        """Creates all tables. """
        self.Model.metadata.create_all(bind=self.engine)
        self.BaseModel.metadata.create_all(bind=self.engine)

    def drop_all(self):
        """Drops all tables. """
        self.Model.metadata.drop_all(bind=self.engine)
        self.BaseModel.metadata.drop_all(bind=self.engine)

    def reflect(self, meta=None):
        """Reflects tables from the database. """
        meta = meta or MetaData()
        meta.reflect(bind=self.engine)
        return meta

    def __repr__(self):
        return "<SQLAlchemy('{0}')>".format(self.uri)
