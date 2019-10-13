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

import os.path
import unittest
import summer


class StringUtilsTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_locate_file(self):
        path = summer.locate_file(__file__, "utilstest.py")
        self.assertEqual(os.path.abspath("utilstest.py"), path)

    def test_ConfigValue(self):
        config_value = summer.ConfigValue()
        path = config_value("PATH", "/usr/bin:/bin")
        self.assertEqual(os.environ["PATH"], path)

        path2 = config_value("PATHXXX", "/usr/bin:/bin")
        self.assertEqual("/usr/bin:/bin", path2)

        port = config_value("PORT", 4444)
        self.assertEqual(4444, port)


if __name__ == "__main__":
    unittest.main()
