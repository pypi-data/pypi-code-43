# copyright 2003-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of CubicWeb.
#
# CubicWeb is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# CubicWeb is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <http://www.gnu.org/licenses/>.
"""unit tests for trustedauth cube"""

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.web import LogOut


class TrustedAuthTC(CubicWebTC):

    def test_login(self):
        req = self.init_authentication('http')
        req.set_request_header('x-remote-user', 'admin', raw=True)
        self.assertAuthSuccess(req)
        self.assertRaises(LogOut, self.app_publish, req, 'logout')
        self.assertEqual(len(self.open_sessions), 0)

    def test_failed_login(self):
        req = self.init_authentication('http')
        req.set_request_header('x-remote-user', 'toto', raw=True)
        self.assertAuthFailure(req)
        req.set_request_header('x-remote-user', 'admin', raw=True)
        self.assertAuthSuccess(req)
        self.assertRaises(LogOut, self.app_publish, req, 'logout')
        self.assertEqual(len(self.open_sessions), 0)


if __name__ == "__main__":
    import unittest
    unittest.main()
