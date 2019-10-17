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

import unittest

from summer import stringutils


class StringUtilsTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_has_text(self):
        self.assertFalse(stringutils.has_text(None))
        obj = "  \t"
        self.assertFalse(stringutils.has_text(obj))
        self.assertTrue(stringutils.has_text(obj, strip=False))
        obj = "summer"
        self.assertTrue(stringutils.has_text(obj))
        obj = " summer\t "
        self.assertTrue(stringutils.has_text(obj))
        self.assertTrue(stringutils.has_text(obj, strip=False))


if __name__ == "__main__":
    unittest.main()
