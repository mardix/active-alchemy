
#Active-SQLAlchemy

**Version 0.3.***

---

Active-SQLAlchemy is a framework agnostic wrapper for SQLAlchemy that makes it really easy
to use by implementing a simple active record like api, while it still uses the db.session underneath.
Inspired by Flask-SQLAlchemy.

Works with Python 2.6, 2.7, 3.3, 3.4 and pypy.

---

##Quick Overview:

####Create the model


    from active_sqlalchemy import SQLAlchemy

    db = SQLAlchemy('sqlite://')

	class User(db.Model):
		name = db.Column(db.String(25))
		location = db.Column(db.String(50), default="USA")
		last_access = db.Column(db.Datetime)


####Create new record


	user = User.create(name="Mardix", location="Moon")
	
	# or
	
	user = User(name="Mardix", location="Moon").save()
	
	
####Get all records

    all = User.all()
    
    
####Get a record by id

    user = User.get(1234)


####Update record

	user = User.get(1234)
	if user:
		user.update(location="Neptune") 


####Soft Delete a record

	user = User.get(1234)
	if user:
		user.delete() 
		
####Query Records

    users = User.all(User.location.distinct())

    for user in users:
        ...


####Query with filter


    all = User.all().filter(User.location == "USA")

    for user in users:
        ...



##How to use


### Install


    pip install active_sqlalchemy


### Create a connection 

The SQLAlchemy class is used to instantiate a SQLAlchemy connection to
a database.


    from active_sqlalchemy import SQLAlchemy

    db = SQLAlchemy(dialect+driver://username:password@host:port/database)

#### Databases Drivers & DB Connection examples

Active-SQLAlchemy comes with a `PyMySQL` and `PG8000` as drivers for MySQL 
and PostgreSQL respectively, because they are in pure Python. But you can use 
other drivers for better performance. `SQLite` is already built in Python. 
  

**SQLite:**

    from active_sqlalchemy import SQLAlchemy

    db = SQLAlchemy("sqlite://") # in memory
    
    # or 
    
    db = SQLAlchemy("sqlite:///foo.db") # DB file
    
**PostgreSql:**

    from active_sqlalchemy import SQLAlchemy

    db = SQLAlchemy("postgresql+pg8000://user:password@host:port/dbname")

**PyMySQL:**

    from active_sqlalchemy import SQLAlchemy

    db = SQLAlchemy("mysql+pymysql://user:password@host:port/dbname")

---


Active-SQLAlchemy also provides access to all the SQLAlchemy
functions from the ``sqlalchemy`` and ``sqlalchemy.orm`` modules.
So you can declare models like the following examples:


### Create a Model

To start, create a model class and extends it with db.Model

	# mymodel.py
	
    from active_sqlachemy import SQLAlchemy

    db = SQLAlchemy("sqlite://")
    
    class MyModel(db.Model):
    	name = db.Column(db.String(25))
    	is_live = db.Column(db.Boolean, default=False)
    	
    # Put at the end of the model module to auto create all models
    db.create_all()


- Upon creation of the table, db.Model will add the following columns: ``id``, ``created_at``, ``upated_at``, ``is_deleted``, ``deleted_at``

- It does an automatic table naming (if no table name is already defined using the ``__tablename__`` property)
by using the class name. So, for example, a ``User`` model gets a table named ``user``, ``TodoList`` becomes ``todo_list``
The name will not be plurialized.

---

## Models: *db.Model*

**db.Model** extends your model with helpers that turn your model into an active record like model. But underneath, it still uses the ``db.session`` 

**db.Model** also adds a few preset columns on the table: 

``id``: The primary key

``created_at``: Datetime. It contains the creation date of the record

``updated_at``: Datetime. It is updated whenever the record is updated.

``deleted_at``: Datetime. Contains the datetime the record was soft-deleted. 

``is_deleted``: Boolean. A flag to set if record is soft-deleted or not

**-- About Soft Delete --**

By definition, soft-delete marks a record as deleted so it doesn't get queried, but it still exists in the database. To actually delete the record itself, a hard delete must apply. 

By default, when a record is deleted, **Active-SQLAlchemy** actually sets ``is_deleted`` to True and excludes it from being queried, and ``deleted_at`` is also set. But this happens only when using the method ``db.Model.delete()``.

When a record is soft-deleted, you can also undelete a record by doing: ``db.Model.delete(False)``

Now, to totally delete off the table, ``db.Model.delete(hard_delete=True)``   


**-- Querying with *db.Model.all()* --**

Due to the fact that **Active-SQLAlchemy** has soft-delete, to query a model without the soft-deleted records, you must query your model by using the ``all(*args, **kwargs)`` which returns a db.session.query object for you to apply filter on etc.


**-- db.BaseModel --**

By default ``db.Model`` adds several preset columns on the table, if you don't want to have them in your model, you can use instead ``db.BaseModel``, which still give you access to the methods to query your model.


---


### db.Model Methods Description

**all(\*args, \*\*kwargs)**

Returns a ``db.session.query`` object to filter or apply more conditions. 

	all = User.all()
	for user in all:
		print(user.login)

By default all() will show only all non-soft-delete records. To display both deleted and non deleted items, add the arg: ``include_deleted=True``

	all = User.all(include_deleted=True)
	for user in all:
		print(user.login)
		
Use all to select columns etc

	all = User.all(User.name.distinct(), User.location)
	for user in all:
		print(user.login)
	
Use all for complete filter

	all = User.all(User.name.distinct, User.location).order_by(User.updated_at.desc()).filter(User.location == "Charlotte")
		
**get(id)**

Get one record by id. By default it will query only a record that is not soft-deleted

	id = 1234
	user = User.get(id)

	print(user.id)
	print(user.login)

To query a record that has been soft deleted, just set the argument ``include_deleted=True``

	id = 234
	user = User.get(id, include_deleted=True)
		
		
**create(\*\*kwargs)**

To create/insert new record. Same as __init__, but just a shortcut to it.

	record = User.create(login='abc', passw_hash='hash', profile_id=123)
	print (record.login) # -> abc

or you can use the __init__ with save()

	record = User(login='abc', passw_hash='hash', profile_id=123).save()
	print (record.login) # -> abc
	
or 

	record = User(login='abc', passw_hash='hash', profile_id=123)
	record.save()
	print (record.login) # -> abc
	
	
**update(\*\*kwargs)**

Update an existing record 

	record = User.get(124)
	record.update(login='new_login')
	print (record.login) # -> new_login

**delete()**

To soft delete a record. ``is_deleted`` will be set to True and ``deleted_at`` datetime will be set

	record = User.get(124)
	record.delete()
	print (record.is_deleted) # -> True
	
To soft UNdelete a record. ``is_deleted`` will be set to False and ``deleted_at`` datetime will be None


	record = User.get(124)
	record.delete(delete=False)
	print (record.is_deleted) # -> False
	
To HARD delete a record. The record will be deleted completely

	record = User.get(124)
	record.delete(hard_delete=True)


**save()**

A shortcut to ``session.add`` + ``session.commit()``

	record = User.get(124)
	record.login = "Another one"
	record.save()

---

#### Method Chaining 

For convenience, some method chaining are available

	user = User(name="Mardix", location="Charlotte").save()
	
	User.get(12345).update(location="Atlanta")
	
	User.get(345).delete().delete(False).update(location="St. Louis")

---


#### Aggegated selects

	class Product(db.Model):
    	name = db.Column(db.String(250))
    	price = db.Column(db.Numeric)
    	
    results = Product.all(db.func.sum(Unit.price).label('price'))


---

## With Web Application

In a web application you need to call ``db.session.remove()`` after each response, and ``db.session.rollback()`` if an error occurs. However, if you are using Flask or other framework that uses the `after_request` and ``on_exception`` decorators, these bindings it is done automatically.

For example using Flask, you can do:


    app = Flask(__name__)

    db = SQLAlchemy('sqlite://', app=app)

or

    db = SQLAlchemy()

    app = Flask(__name__)

    db.init_app(app)


### More examples

####Many databases, one web app


    app = Flask(__name__)
    db1 = SQLAlchemy(URI1, app)
    db2 = SQLAlchemy(URI2, app)


####Many web apps, one database


    db = SQLAlchemy(URI1)

    app1 = Flask(__name__)
    app2 = Flask(__name__)
    db.init_app(app1)
    db.init_app(app2)

        
---

## Pagination

All the results can be easily paginated

    users = User.paginate(page=2, per_page=20)
    print(list(users))  # [User(21), User(22), User(23), ... , User(40)]


The paginator object it's an iterable that returns only the results for that page, so you use it in your templates in the same way than the original result:



    {% for item in paginated_items %}
        <li>{{ item.name }}</li>
    {% endfor %}


Rendering the pages

Below your results is common that you want it to render the list of pages.

The ``paginator.pages`` property is an iterator that returns the page numbers, but sometimes not all of them: if there are more than 11 pages, the result will be one of these, depending of what is the current page:


Skipped page numbers are represented as ``None``.

How many items are displayed can be controlled calling ``paginator.iter_pages`` instead.

This is one way how you could render such a pagination in your templates:



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

####Credits:

[SQLAlchemy](http://www.sqlalchemy.org/)

[Flask-SQLAlchemy](https://pythonhosted.org/Flask-SQLAlchemy)

[SQLAlchemy-Wrapper](https://github.com/lucuma/sqlalchemy-wrapper)

---

copyright: 2015

license: MIT, see LICENSE for more details.
