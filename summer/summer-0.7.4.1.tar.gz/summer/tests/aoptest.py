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
import summer


class CustomManager(object):
    @summer.transactional
    def sample_tx_method(self):
        """Sample tx method."""

    @summer.ldapaop
    def sample_ldap_method(self):
        """Sample ldap method."""


class AopTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_aop(self):
        method = CustomManager.sample_tx_method
        self.assertEqual("Sample tx method.", method.__doc__)
        self.assertEqual(method.__doc__, method.__wrapped__.__doc__)

        method = CustomManager.sample_ldap_method
        self.assertEqual("Sample ldap method.", method.__doc__)
        self.assertEqual(method.__doc__, method.__wrapped__.__doc__)


if __name__ == "__main__":
    unittest.main()
