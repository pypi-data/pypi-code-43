# appteka - helpers collection

# Copyright (C) 2018-2019 Aleksandr Popov

# This program is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Lesser GNU General Public License for more details.

# You should have received a copy of the Lesser GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Helper for TDD of sqlite3 schema."""

import sqlite3


class TestSchemaHelper:
    """This class holds sqlite3 connection and cursor.

    Parameters
    ----------
    test_case: object
        Instance of test case.
    """
    def __init__(self, test_case):
        self._conn = sqlite3.connect(":memory:")
        self._cur = self._conn.cursor()
        self._test_case = test_case

    def test_select(self, query, ref):
        """Execute select query and compare result with reference one."""
        res = list(self._cur.execute(query))
        self._test_case.assertEqual(res, ref)

    def dot_read(self, path):
        """Execute all queries from path."""
        with open(path) as buf:
            script = buf.read()

        queries = script.split(";")

        for query in queries:
            self._cur.execute(query)

    def close(self):
        """Close connection with database."""
        self._conn.close()
