
# Active-Alchemy

**Version 1.x.x***

---

Active-Alchemy is wrapper around SQLAlchemy that makes it simple to use 
your models in an active record like manner, while it still uses the SQLAlchemy `db.session` underneath.

Active-Alchemy was created as solution to use my flask's application's model 
without the need to use Flask-SQLAlchemy outside of Flask projects.


What you may like about Active-Alchemy:

- Just by instantiating with `ActiveAlchemy()`, ActiveAlchemy automatically creates
the session, model and everything necessary for SQLAlchemy.
- It provides easy methods such as `query()`, `create()`, `update()`, `delete()`,
 to select, create, update, delete entries respectively.   
- It automatically create a primary key for your table
- It adds the following columns: `id`, `created_at`, `updated_at`, `is_deleted`, `deleted_at`
- When `delete()`, it soft deletes the entry so it doesn't get queried. But it still
exists in the database. This feature allows you to un-delete an entry
- It uses Arrow for DateTime
- DateTime is saved in UTC and uses the ArrowType from the SQLAlchemy-Utils
- Added some data types: JSONType, EmailType, and the whole SQLAlchemy-Utils Type
- db.now -> gives you the Arrow UTC type
- It is still SQLAlchemy. You can access all the SQLAlchemy awesomeness

---

## Quick Overview:

#### Create the model

    from active_alchemy import ActiveAlchemy

    db = ActiveAlchemy('sqlite://')

	class User(db.Model):
		name = db.Column(db.String(25))
		location = db.Column(db.String(50), default="USA")
		last_access = db.Column(db.Datetime)

	
#### Retrieve all records

    for user in User.query():
        print(user.name)
    
    
#### Create new record

	user = User.create(name="Mardix", location="Moon")
	
	# or
	
	user = User(name="Mardix", location="Moon").save()

    
#### Get a record by primary key (id)

    user = User.get(1234)


#### Update record from primary key

	user = User.get(1234)
	if user:
		user.update(location="Neptune") 

#### Update record from query iteration

	for user in User.query():
		user.update(last_access=db.utcnow());
		

#### Soft Delete a record

	user = User.get(1234)
	if user:
		user.delete() 
		
#### Query Records

    users = User.query(User.location.distinct())

    for user in users:
        ...


#### Query with filter


    all = User.query().filter(User.location == "USA")

    for user in users:
        ...


## How to use


### Install


    pip install active_alchemy


### Create a connection 

The `ActiveAlchemy` class is used to instantiate a SQLAlchemy connection to
a database.


    from active_alchemy import ActiveAlchemy

    db = ActiveAlchemy(dialect+driver://username:password@host:port/database)

#### Databases Drivers & DB Connection examples

Active-Alchemy comes with a `PyMySQL` and `PG8000` as drivers for MySQL 
and PostgreSQL respectively, because they are in pure Python. But you can use 
other drivers for better performance. `SQLite` is already built in Python. 
  

**SQLite:**

    from active_alchemy import ActiveAlchemy

    db = ActiveAlchemy("sqlite://") # in memory
    
    # or 
    
    db = ActiveAlchemy("sqlite:///foo.db") # DB file
    
**PostgreSql:**

    from active_alchemy import ActiveAlchemy

    db = ActiveAlchemy("postgresql+pg8000://user:password@host:port/dbname")

**PyMySQL:**

    from active_alchemy import ActiveAlchemy

    db = ActiveAlchemy("mysql+pymysql://user:password@host:port/dbname")

---


Active-Alchemy also provides access to all the SQLAlchemy
functions from the ``sqlalchemy`` and ``sqlalchemy.orm`` modules.
So you can declare models like the following examples:


### Create a Model

To start, create a model class and extends it with db.Model

	# mymodel.py
	
    from active_alchemy import ActiveAlchemy

    db = ActiveAlchemy("sqlite://")
    
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

By default, when a record is deleted, **Active-Alchemy** actually sets ``is_deleted`` to True and excludes it from being queried, and ``deleted_at`` is also set. But this happens only when using the method ``db.Model.delete()``.

When a record is soft-deleted, you can also undelete a record by doing: ``db.Model.delete(False)``

Now, to completely delete off the table, ``db.Model.delete(hard_delete=True)``   


**-- Querying with *db.Model.query()* --**

Due to the fact that **Active-Alchemy** has soft-delete, to query a model without the soft-deleted records, you must query your model by using the ``all(*args, **kwargs)`` which returns a db.session.query object for you to apply filter on etc.


**-- db.BaseModel --**

By default ``db.Model`` adds several preset columns on the table, if you don't want to have them in your model, you can use instead ``db.BaseModel``, which still give you access to the methods to query your model.

``BaseModel`` by default assumes that your primary key is ``id``, but it 

    class MyExistingModel(db.BaseModel):
        __tablename__ = "my_old_table"
        __primary_key__  = "my_pk_id"
        
        my_pk_id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String)
        ...

---


### db.Model Methods Description

#### query(\*args, \*\*kwargs)

To start querying the DB and returns a ``db.session.query`` object to filter or apply more conditions.

	for user in User.query():
		print(user.login)

By default `query()` will show only all non-soft-delete records. To display both deleted and non deleted items, add the arg: ``include_deleted=True``

	for user in User.query(include_deleted=True):
		print(user.login)
		
To select columns...

	for user in User.query(User.name.distinct(), User.location):
		print(user.login)
	
To use with filter...

	all = User
	        .query(User.name.distinct, User.location)
	        .order_by(User.updated_at.desc())
	        .filter(User.location == "Charlotte")
		
#### get(id)

Get one record by id. By default it will query only a record that is not soft-deleted

	id = 1234
	user = User.get(id)
	print(user.id)
	print(user.login)

To query a record that has been soft deleted, just set the argument ``include_deleted=True``

	id = 234
	user = User.get(id, include_deleted=True)
		
		
#### create(\*\*kwargs)

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
	
	
#### update(\*\*kwargs)

Update an existing record 

	record = User.get(124)
	record.update(login='new_login')
	print (record.login) # -> new_login

#### delete()

To soft delete a record. ``is_deleted`` will be set to True and ``deleted_at`` datetime will be set

	record = User.get(124)
	record.delete()
	print (record.is_deleted) # -> True
	
To soft **UNdelete** a record. ``is_deleted`` will be set to False and ``deleted_at`` datetime will be None


	record = User.get(124)
	record.delete(delete=False)
	print (record.is_deleted) # -> False
	
To HARD delete a record. The record will be deleted completely

	record = User.get(124)
	record.delete(hard_delete=True)


#### save()

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
    	
    price_label = db.func.sum(Product.price).label('price')
    results = Product.query(price_label)

---

## With Web Application

In a web application you need to call ``db.session.remove()`` after each response, and ``db.session.rollback()`` if an error occurs. However, if you are using Flask or other framework that uses the `after_request` and ``on_exception`` decorators, these bindings it is done automatically.

For example using Flask, you can do:


    app = Flask(__name__)

    db = ActiveAlchemy('sqlite://', app=app)

or

    db = ActiveAlchemy()

    app = Flask(__name__)

    db.init_app(app)


### More examples

#### Many databases, one web app


    app = Flask(__name__)
    db1 = ActiveAlchemy(URI1, app)
    db2 = ActiveAlchemy(URI2, app)


#### Many web apps, one database


    db = ActiveAlchemy(URI1)

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



    {% macro pagination(paginator, endpoint=None, class_='pagination') %}
        {% if not endpoint %}
            {% set endpoint = request.endpoint %}
        {% endif %}
        {% if "page" in kwargs %}
            {% do kwargs.pop("page") %}
        {% endif %}
        <nav>
            <ul class="{{ class_ }}">
              {%- if paginator.has_prev %}
                <li><a href="{{ url_for(endpoint, page=paginator.prev_page_number, **kwargs) }}"
                 rel="me prev"><span aria-hidden="true">&laquo;</span></a></li>
              {% else %}
                <li class="disabled"><span><span aria-hidden="true">&laquo;</span></span></li>
              {%- endif %}
    
              {%- for page in paginator.pages %}
                {% if page %}
                  {% if page != paginator.page %}
                    <li><a href="{{ url_for(endpoint, page=page, **kwargs) }}"
                     rel="me">{{ page }}</a></li>
                  {% else %}
                    <li class="active"><span>{{ page }}</span></li>
                  {% endif %}
                {% else %}
                  <li><span class=ellipsis>…</span></li>
                {% endif %}
              {%- endfor %}
    
              {%- if paginator.has_next %}
                <li><a href="{{ url_for(endpoint, page=paginator.next_page_number, **kwargs) }}"
                 rel="me next">»</a></li>
              {% else %}
                <li class="disabled"><span aria-hidden="true">&raquo;</span></li>
              {%- endif %}
            </ul>
        </nav>
    {% endmacro %}

______

#### Credits:

[SQLAlchemy](http://www.sqlalchemy.org/)

[Flask-SQLAlchemy](https://pythonhosted.org/Flask-SQLAlchemy)

[SQLAlchemy-Wrapper](https://github.com/lucuma/sqlalchemy-wrapper)

[Paginator](https://github.com/mardix/paginator.py)

[Arrow](http://crsmithdev.com/arrow/)

[SQLAlchemy-Utils](https://sqlalchemy-utils.readthedocs.io)

---

copyright: 2015-2016

license: MIT, see LICENSE for more details.
