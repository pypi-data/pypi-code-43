# -*- coding: utf-8 -*-
# Time-stamp: < sftest.py (2017-07-05 08:41) >

# Copyright (C) 2009-2019 Martin Slouf <martinslouf@users.sourceforge.net>
#
# This file is a part of Summer.
#
# Summer is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import threading
import unittest

from summer.tests.appcontext import ctx


class DaoTestThread(threading.Thread):
    def __init__(self, sf):
        threading.Thread.__init__(self)
        self.sf = sf
        self.sql_alchemy_session = None

    def run(self):
        self.sql_alchemy_session = self.sf.sqlalchemy_session


class SfTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sqlalchemy_session_in_threads(self):
        sf = ctx.session_factory
        self.assertIsNotNone(sf)

        s1 = sf.sqlalchemy_session
        s2 = sf.sqlalchemy_session
        self.assertTrue(s1 is s2)

        thread = DaoTestThread(sf)
        thread.start()
        thread.join()
        self.assertTrue(s1 is not thread.sql_alchemy_session)

    def test_connection(self):
        sf = ctx.session_factory
        self.assertIsNotNone(sf)

        query = "CREATE TABLE person (name TEXT, age INT)"
        dbcon = sf.connection.connection
        cursor = dbcon.cursor()
        cursor.execute(query)

        query = "INSERT INTO person (name, age) VALUES (?, ?)"
        for i in range(1, 9):
            tmp = {"name": "name_%d" % i, "age": i}
            cursor.execute(query, (tmp["name"], tmp["age"]))
        dbcon.commit()

        query = "SELECT * FROM person"
        cursor.execute(query)
        idx = 1
        row = cursor.fetchone()
        while row:
            self.assertEqual(row[0], "name_%d" % idx)
            self.assertEqual(row[1], idx)
            idx += 1
            row = cursor.fetchone()
        dbcon.commit()

    def test_sqlite_dialect(self):
        self.assertTrue(ctx.session_factory.sqlite_dialect)


if __name__ == "__main__":
    unittest.main()
