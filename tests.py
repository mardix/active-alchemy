from active_alchemy import ActiveAlchemy
import unittest

table_name = "test_model"

class TestActiveAlchemy(unittest.TestCase):

    @staticmethod
    def create_test_model(db):
        class TestModel(db.Model):
            #__tablename__ = "test_model"
            name = db.Column(db.String(20))
            location = db.Column(db.String(20))

        class BaseTestModel(db.BaseModel):
            __tablename__ = "test_model"
            __primary_key__ = "id"

            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(20))
            location = db.Column(db.String(20))
        db.create_all()

        return TestModel, BaseTestModel

    def setUp(self):
        uri = 'sqlite://'
        self.db = ActiveAlchemy(uri)
        self.model, self.base_model = self.create_test_model(self.db)


    def tearDown(self):
        self.db.query(self.model).delete()
        self.db.commit()

    def add_entry(self):
        return self.model(name="Max", location="Charlotte").save()

    def test_init_save(self):
        e = self.add_entry()
        self.assertIsNotNone(e)

    def test_table_name(self):
        self.assertEquals(table_name, self.model.__table__.name)

    def test_create(self):
        data = {
            "name": "Jones",
            "location": "Miami"
        }
        self.assertIs(0, len(list(self.model.query())))

        v = self.add_entry()
        self.assertIs(1, len(list(self.model.query())))

        e = v.create(**data)
        self.assertIsNotNone(e)
        self.assertIs(2, len(list(self.model.query())))

        e.update(location="Japan")
        self.assertEquals(e.location, "Japan")

    def test_update(self):
        n_loc = "ATL"
        e = self.add_entry()
        e.update(location=n_loc)
        self.assertEqual(n_loc, e.location)

    def test_delete(self):
        e = self.add_entry()
        e.delete()
        self.assertTrue(e.is_deleted)

    def test_undelete(self):
        e = self.add_entry()
        e.delete()
        self.assertTrue(e.is_deleted)
        e.delete(False)
        self.assertFalse(e.is_deleted)

    def test_delete_hard(self):
        e = self.add_entry()
        self.assertIs(1, len(list(self.model.query())))
        e.delete(hard_delete=True)
        self.assertIs(0, len(list(self.model.query(include_deleted=True))))


    def test_get(self):
        e = self.add_entry()
        self.assertIsNotNone(self.model.get(e.id))

    def test_get_basemodel(self):
        e = self.add_entry()
        self.assertIsNotNone(self.base_model.get(e.id))

    def test_get_deleted(self):
        e = self.add_entry().delete()
        self.assertIsNone(self.model.get(e.id))
        self.assertIsNotNone(self.model.get(e.id, include_deleted=True))

    def test_query(self):
        self.add_entry()
        self.add_entry()
        self.add_entry()
        self.add_entry()
        self.add_entry()
        self.assertIs(5, len(list(self.model.query())))

    def test_all_but_deleted(self):
        self.add_entry()
        self.add_entry()
        self.add_entry().delete()
        self.add_entry().delete()
        self.add_entry()
        self.assertIs(3, len(list(self.model.query())))

    def test_all_but_undeleted(self):
        self.add_entry()
        self.add_entry()
        self.add_entry().delete()
        self.add_entry().delete().delete(False)
        self.add_entry()

        self.assertIs(4, len(list(self.model.query())))
        self.assertIs(5, len(list(self.model.query(include_deleted=True))))

    def test_to_dict(self):
        e = self.add_entry()
        self.assertIsInstance(e.to_dict(), dict)

    def test_to_json(self):
        e = self.add_entry()
        self.assertIsInstance(e.to_json(), str)

    def test_all_distinct(self):
        for n in xrange(15):
            self.add_entry()
        es = self.model.query(self.model.name.distinct())
        self.assertIs(1, len(list(es)))

    def test_paginate(self):
        for n in xrange(15):
            self.add_entry()

        es = self.model.query().paginate(page=2, per_page=4)
        self.assertIs(4, es.total_pages)


if __name__ == '__main__':
    unittest.main()

