import unittest
import unittest.mock

def setUpModule():
    pass

def tearDownModule():
    pass

class SqLiteTestCase(unittest.TestCase):
    db_test_file = "./test.sqlite"

    @classmethod
    def clean_test_db(cls):
        import os
        if os.path.exists(cls.db_test_file):
            os.remove(cls.db_test_file)

    @classmethod
    def setUpClass(cls):
        from fairways.ci import helpers
        cls.helpers = helpers

        from fairways.io.asyn import sqlite

        import asyncio
        import time
        import concurrent.futures
        import re
        import os
        cls.asyncio = asyncio
        cls.sqlite = sqlite
        cls.time = time
        cls.futures = concurrent.futures
        cls.re = re

        cls.clean_test_db()
        root = helpers.getLogger()

    @classmethod
    def tearDownClass(cls):
        cls.clean_test_db()

    def test_select_const(self):
        """
        """
        sqlite = self.sqlite
        asyncio = self.asyncio

        # default=":memory:"
        db_alias = "MY_TEST_SQLITE"

        with unittest.mock.patch.dict('os.environ', {db_alias: ":memory:"}, clear=True):
            db = sqlite.SqLite(db_alias)

            sql = "select 99"
            result = self.helpers.run_asyn(db.fetch(sql))

        self.assertEqual(result, [{'99': 99}])

    def test_create_read(self):
        """
        """
        sqlite = self.sqlite

        db_alias = "MY_TEST_SQLITE"

        with unittest.mock.patch.dict('os.environ', {db_alias: self.db_test_file}, clear=True):
            db = sqlite.SqLite(db_alias)

            sql = """CREATE TABLE fairways (id integer primary key, name varchar);"""
            
            self.helpers.run_asyn(db.execute(sql))

            sql = """insert into fairways (id, name) values (1, "My Way");"""
            
            self.helpers.run_asyn(db.execute(sql))

            sql = """select name from fairways where id=1;"""
            
            result = self.helpers.run_asyn(db.fetch(sql))
            
        self.assertEqual(result, [{'name': 'My Way'}])

