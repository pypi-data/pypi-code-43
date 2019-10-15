# copyright 2010-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""plugin authentication retriever

:organization: Logilab
:copyright: 2010-2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""

__docformat__ = "restructuredtext en"

from cubicweb import AuthenticationError
from cubicweb.server.sources import native


class XRemoteUserAuthentifier(native.BaseAuthentifier):

    def authenticate(self, session, login, **kwargs):
        """return CWUser eid for the given login (coming from x-remote-user
        http headers) if this account is defined in this source,
        else raise `AuthenticationError`
        """
        session.debug('authentication by %s', self.__class__.__name__)
        if 'trustedauth_login' in kwargs:
            rset = session.execute(
                'Any U WHERE U is CWUser, U login %(trustedauth_login)s',
                kwargs)
            if rset:
                return rset[0][0]
        raise AuthenticationError('no trusted authentication for this user')
