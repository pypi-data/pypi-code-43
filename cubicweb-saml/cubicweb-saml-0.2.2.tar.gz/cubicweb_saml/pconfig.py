# copyright 2019 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

__docformat__ = "restructuredtext en"

from zope.interface import implementer

from pyramid.authentication import IAuthenticationPolicy
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.security import remember
from pyramid.view import view_config

from cubicweb.pyramid.auth import CWAuthTktAuthenticationPolicy

from cubicweb_saml.utils import get_user, retrieve_url_from_client


@view_config(route_name='saml')
def saml(request):
    """ Manage SAML requests and show an error message when the SAML user is
    not available in cubicweb.
    """
    if request.POST and 'SAMLResponse' in request.POST:
        userid = get_user(request)
        if userid:
            raise HTTPSeeOther(location=request.cw_request.build_url(
                                   request.POST.get('RelayState', '')),
                               headers=remember(request, userid))

        request.cw_request.set_message(
            request.cw_request._('Authentication with SAML failed.'))
        request.response.status_code = 403
        raise HTTPSeeOther(location=request.cw_request.build_url('login'))

    raise HTTPSeeOther(location=request.cw_request.build_url(''))


@implementer(IAuthenticationPolicy)
class SAMLAuthenticationPolicy(CWAuthTktAuthenticationPolicy):

    def authenticated_userid(self, request):
        """ Return the authenticated userid or None if no authenticated userid
        can be found. This method of the policy should ensure that a record
        exists in whatever persistent store is used related to the user (the
        user should not have been deleted); if a record associated with the
        current id does not exist in a persistent store, it should return None.
        """
        if '__login' in request.POST and not request.POST.get('__login', ''):

            if 'SAMLResponse' not in request.POST:
                raise HTTPSeeOther(location=retrieve_url_from_client(
                    request.registry['cubicweb.config'], request))

            userid = get_user(request)
            if userid:
                return str(userid)

        super(SAMLAuthenticationPolicy, self).authenticated_userid(request)
