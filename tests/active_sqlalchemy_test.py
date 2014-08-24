from active_sqlalchemy import SQLAlchemy
import unittest


class TestActiveSqlAlchemy(unittest.TestCase):

    @staticmethod
    def create_test_model(db):
        class TestModel(db.ActiveModel):
            #__tablename__ = "test_model"
            name = db.Column(db.String(20))
            location = db.Column(db.String(20))
        db.create_all()

        return TestModel

    def setUp(self):
        uri = 'sqlite://'
        self.db = SQLAlchemy(uri)
        self.model = self.create_test_model(self.db)

    def tearDown(self):
        self.db.query(self.model).delete()
        self.db.commit()

    def add_entry(self):
        return self.model(name="Max", location="Charlotte").save()

    def test_init_save(self):
        e = self.add_entry()
        self.assertIsNotNone(e)

    def test_get_table_name_when_unassigned(self):
        self.assertEquals("test_model", self.model.__table__.name)

    def test_insert(self):
        data = {
            "name": "Jones",
            "location": "Miami"
        }
        self.assertIs(0, len(list(self.model.all())))

        v = self.add_entry()
        self.assertIs(1, len(list(self.model.all())))

        e = v.insert(**data)
        self.assertIsNotNone(e)
        self.assertIs(2, len(list(self.model.all())))

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
        self.assertIs(1, len(list(self.model.all())))
        e.delete(hard_delete=True)
        self.assertIs(0, len(list(self.model.all(exclude_deleted=False))))


    def test_get(self):
        e = self.add_entry()
        self.assertIsNotNone(self.model.get(e.id))

    def test_get_deleted(self):
        e = self.add_entry().delete()
        self.assertIsNone(self.model.get(e.id))
        self.assertIsNotNone(self.model.get(e.id, exclude_deleted=False))

    def test_all(self):
        self.add_entry()
        self.add_entry()
        self.add_entry()
        self.add_entry()
        self.add_entry()
        self.assertIs(5, len(list(self.model.all())))

    def test_all_but_deleted(self):
        self.add_entry()
        self.add_entry()
        self.add_entry().delete()
        self.add_entry().delete()
        self.add_entry()

        self.assertIs(3, len(list(self.model.all())))

    def test_all_but_undeleted(self):
        self.add_entry()
        self.add_entry()
        self.add_entry().delete()
        self.add_entry().delete().delete(False)
        self.add_entry()

        self.assertIs(4, len(list(self.model.all())))
        self.assertIs(5, len(list(self.model.all(exclude_deleted=False))))

    def test_to_dict(self):
        e = self.add_entry()
        self.assertIsInstance(e.to_dict(), dict)

    def test_to_json(self):
        e = self.add_entry()
        self.assertIsInstance(e.to_json(), str)

    def test_all_distinct(self):
        for n in xrange(15):
            self.add_entry()
        es = self.model.all(self.model.name.distinct())
        self.assertIs(1, len(list(es)))

    def test_paginate(self):
        for n in xrange(15):
            self.add_entry()

        es = self.model.all().paginate(page=2, per_page=4)
        self.assertIs(4, len(list(es)))


if __name__ == '__main__':
    unittest.main()
