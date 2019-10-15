# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-trustedauth pyramid_cubiweb integration module

"""

import logging

from zope.interface import implementer
from pyramid.authentication import IAuthenticationPolicy

logger = logging.getLogger(__name__)

# we cannot really use the RemoteUserAuthenticationPolicy here since
# it does **not** return the result of the callback -- where we could
# have done the login => eid translation -- call as
# authenticated_userid (pyramid_cubicweb expects this method to return
# a CWUser eid).


@implementer(IAuthenticationPolicy)
class TrustedAuthenticationPolicy(object):

    def __init__(self, environ_key='HTTP_X_REMOTE_USER'):
        self.environ_key = environ_key

    def unauthenticated_userid(self, request):
        return None

    def authenticated_userid(self, request):
        login = request.environ.get(self.environ_key)
        if login is None:
            return
        repo = request.registry['cubicweb.repository']
        with repo.internal_cnx() as cnx:
            try:
                rset = cnx.execute('Any U WHERE U is CWUser, U login %(login)s',
                                   {'login': login})
                if rset:
                    assert len(rset) == 1
                    logger.debug('%s: authenticated %s (%s)', self.__class__.__name__, login, rset[0][0])
                    return rset[0][0]
            except Exception as exc:
                logger.debug('%s: authentication failure (%s)', self.__class__.__name__, exc)
        return None

    def remember(self, request, principal, **kw):
        """ A no-op. The ``REMOTE_USER`` does not provide a protocol for
        remembering the user. This will be application-specific and can
        be done somewhere else or in a subclass."""
        return ()

    def forget(self, request):
        """ A no-op. The ``REMOTE_USER`` does not provide a protocol for
        forgetting the user. This will be application-specific and can
        be done somewhere else or in a subclass."""
        return ()
