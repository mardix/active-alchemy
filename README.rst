===========================
Active-SQLAlchemy
===========================

A framework-independent wrapper for SQLAlchemy that makes it really easy to use.

Works with Python 2.6, 2.7, 3.3, 3.4 and pypy.


###Example:

Create the model

.. code:: python

    from active_sqlalchemy import SQLAlchemy

    db = SQLAlchemy('pymysql://user:password@host:port/mydatabase')

	class User(db.ActiveModel):
		name = db.Column(db.String(25))
		location = db.Column(db.String(50), default="USA")
		last_access = db.Column(db.Datetime)

Insert new record

.. code:: python

	user = User.insert(name="John", location="Moon")
	
	# or
	
	user = User(name="John", location="Moon").save()
	
	
Get all records

.. code:: python

    all = User.all()
    
Get a record by id

.. code:: python

    user = User.get(1234)

Update record

.. code:: python

	user = User.get(1234)
	if user:
		user.update(location="Neptune") 

Soft Delete a record

.. code:: python

	user = User.get(1234)
	if user:
		user.delete() 
		
To query

.. code:: python

    users = User.all(User.location.distinct())

    for user in users:
        ...


To query with filter

.. code:: python

    all = User.all().filter(User.location == "USA")

    for user in users:
        ...



How to use
========================

### Install

.. code:: python

    pip install active_sqlalchemy


PIP install directly from Github

.. code:: python

    pip install https://github.com/mardix/active-sqlalchemy/archive/master.zip


### Create a connection 

The SQLAlchemy class is used to instantiate a SQLAlchemy connection to
a database.

.. code:: python

    from active_sqlalchemy import SQLAlchemy

    db = SQLAlchemy(_uri_to_database_)


The class also provides access to all the SQLAlchemy
functions from the ``sqlalchemy`` and ``sqlalchemy.orm`` modules.
So you can declare models like this:

---

## Create a Model

To start, create a model class and extends it with db.ActiveModel

.. code:: python

	# model.py
	
    from sqlalchemy_wrapper2 import SQLAlchemy

    db = SQLAlchemy("pymysql://user:pass@host:port/dbname")
    
    class MyModel(db.ActiveModel):
    	name = db.Column(db.String(25))
    	is_live = db.Column(db.Boolean, default=False)
    	
    # Put at the end of the model module to auto create all models
    db.create_all()


- Upon creation of the table, db.ActiveModel will add the following columns: ``id``, ``created_at``, ``upated_at``, ``is_deleted``, ``deleted_at``

- It does an automatic table naming (if no table name is already defined using the ``__tablename__`` property)  by using the class name using the `inflection <http://inflection.readthedocs.org>`_ library. So, for example, a ``User`` model gets a table named ``user``, ``TodoList`` becomes ``todo_list``
The name will not be plurialized.


## db.ActiveModel

**db.ActiveModel** extends the model with some cool helper method that will allow you to get, save, update in the current model instead of using ``db.session``. It turns the model into a 'quasi' active-record.

**db.ActiveModel** also adds a few preset columns in the table: ``id``, ``created_at``, ``upated_at``, ``is_deleted``, ``deleted_at``

**SOFT DELETE RECORD**: by default db.Model soft delete record by setting ``is_deleted`` to True using the method ``delete(delete_record=True)``. It also assign  the datetime  to ``deleted_at``. When ``delete(delete_record=False)`` is False, ``deleted_at`` will be set to None

*Use db.ActiveModel for new tables that will have the same structure. It also offers a quasi active-record like on the records*


.. code:: python

    class User(db.ActiveModel):
        login = db.Column(db.Unicode, unique=True)
        passw_hash = db.Column(db.Unicode)
        profile_id = db.Column(db.Integer, db.ForeignKey(Profile.id))
        profile = db.relationship(Profile, backref=db.backref('user'))


### Methods Description

**all(exclude_deleted=True, \*args, \*\*kwargs)**

Returns a ``session.query`` object to filter or apply more conditions. 

.. code:: python

	all = User.all()
	for user in all:
		print(user.login)

By default all() will show only all non-soft-delete items. To display both deleted and non deleted items, add the arg: exclude_deleted=False

.. code:: python

	all = User.all(exclude_deleted=False)
	for user in all:
		print(user.login)
		
Use all to select columns etc

.. code:: python

	all = User.all(User.name.distinct, User.location)
	
	
Use all for complete filter

.. code:: python

	all = User.all(User.name.distinct, User.location).order_by(User.updated_at.desc()).filter(User.location == "Charlotter")
		
**get(id, exclude_deleted=True)**

Get one record by id. By default it will query only a record that is not soft-deleted

.. code:: python

	id = 1234
	user = User.get(id)

	print(user.id)
	print(user.login)

		
		
**insert(\*\*kwargs)**

To insert new record. Same as init, but just a shortcut to it.

.. code:: python

	record = User.insert(login='abc', passw_hash='hash', profile_id=123)
	print (record.login) # -> abc

or you can use the shortcut 

.. code:: python

	record = User(login='abc', passw_hash='hash', profile_id=123)
	record.save()
	print (record.login) # -> abc
	
**update(\*\*kwargs)**

Update an existing record 

.. code:: python

	record = User.get(124)
	record.update(login='new_login')
	print (record.login) # -> new_login

**delete()**

To soft delete a record. ``is_deleted`` will be set to True and ``deleted_at`` datetime will be set

.. code:: python

	record = User.get(124)
	record.delete()
	print (record.is_deleted) # -> True
	
To soft UNdelete a record. ``is_deleted`` will be set to False and ``deleted_at`` datetime will be set

.. code:: python

	record = User.get(124)
	record.delete(delete=False)
	print (record.is_deleted) # -> False
	
To soft HARD delete a record. The record will be deleted completely

.. code:: python

	record = User.get(124)
	record.delete(hard_delete=True)

**save()**

A shortcut to ``session.add`` + ``session.commit()``

.. code:: python

	record = User.get(124)
	record.login = "Another one"
	record.save()

---


### db.Model

**db.Model** doesn't add any columns by default, but it will auto-create the ``__tablename__`` if it is not set.

*Use db.Model for existing table model, or when you don't need the preset columns*

.. code:: python

    class User(db.Model):
    	id = db.Column(db.Integer, primary_key=True)
        login = db.Column(db.Unicode, unique=True)
        passw_hash = db.Column(db.Unicode)
        profile_id = db.Column(db.Integer, db.ForeignKey(Profile.id))
        profile = db.relationship(Profile, backref=db.backref('user'))
        
---	

## Active SQLAlchemy With Web Application

In a web application you need to call ``db.session.remove()`` after each response, and ``db.session.rollback()`` if an error occurs. However, if you are using Flask or other framework that uses the `after_request` and ``on_exception`` decorators, these bindings it is done automatically:

.. code:: python

    app = Flask(__name__)

    db = SQLAlchemy('sqlite://', app=app)

or

.. code:: python

    db = SQLAlchemy()

    app = Flask(__name__)

    db.init_app(app)


### More examples


Many databases, one web app

.. code:: python

    app = Flask(__name__)
    db1 = SQLAlchemy(URI1, app)
    db2 = SQLAlchemy(URI2, app)


Many web apps, one database

.. code:: python

    db = SQLAlchemy(URI1)

    app1 = Flask(__name__)
    app2 = Flask(__name__)
    db.init_app(app1)
    db.init_app(app2)


Aggegated selects

.. code:: python

    res = db.query(db.func.sum(Unit.price).label('price')).all()
    print res.price


Mixins

.. code:: python

    class IDMixin(object):
        id = db.Column(db.Integer, primary_key=True)

.. code:: python

    class Model(IDMixin, db.Model):
        field = db.Column(db.Unicode)


### Pagination

All the results can be easily paginated

.. code:: python

    users = User.paginate(page=2, per_page=20)
    print(list(users))  # [User(21), User(22), User(23), ... , User(40)]


The paginator object it's an iterable that returns only the results for that page, so you use it in your templates in the same way than the original result:

.. code:: python

    {% for item in paginated_items %}
        <li>{{ item.name }}</li>
    {% endfor %}


Rendering the pages

Below your results is common that you want it to render the list of pages.

The ``paginator.pages`` property is an iterator that returns the page numbers, but sometimes not all of them: if there are more than 11 pages, the result will be one of these, depending of what is the current page:


Skipped page numbers are represented as ``None``.

How many items are displayed can be controlled calling ``paginator.iter_pages`` instead.

This is one way how you could render such a pagination in your templates:

.. code:: python

    {% macro render_paginator(paginator, endpoint) %}
      <p>Showing {{ paginator.showing }} or {{ paginator.total }}</p>

      <ol class="paginator">
      {%- if paginator.has_prev %}
        <li><a href="{{ url_for(endpoint, page=paginator.prev_num) }}"
         rel="me prev">«</a></li>
      {% else %}
        <li class="disabled"><span>«</span></li>
      {%- endif %}

      {%- for page in paginator.pages %}
        {% if page %}
          {% if page != paginator.page %}
            <li><a href="{{ url_for(endpoint, page=page) }}"
             rel="me">{{ page }}</a></li>
          {% else %}
            <li class="current"><span>{{ page }}</span></li>
          {% endif %}
        {% else %}
          <li><span class=ellipsis>…</span></li>
        {% endif %}
      {%- endfor %}

      {%- if paginator.has_next %}
        <li><a href="{{ url_for(endpoint, page=paginator.next_num) }}"
         rel="me next">»</a></li>
      {% else %}
        <li class="disabled"><span>»</span></li>
      {%- endif %}
      </ol>
    {% endmacro %}

______

:copyright: © 2014 
:license: MIT, see LICENSE for more details.
