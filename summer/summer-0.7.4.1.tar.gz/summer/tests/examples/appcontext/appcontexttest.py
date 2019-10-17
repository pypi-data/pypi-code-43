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

"""Most simple standalone example.

Look at the single :py:mod:`appcontext` module.

"""

import unittest
from summer.tests.examples.appcontext.appcontext import ctx


class AppContextTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_appcontext(self):
        self.assertIsNotNone(ctx.session_factory)
        self.assertIsNone(ctx.ldap_session_factory)
        ctx.entity_manager.find()


if __name__ == "__main__":
    unittest.main()
