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

from requests import get as requests_get

from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from saml2.client import Saml2Client
from saml2.config import Config
from saml2.entity import BINDING_HTTP_POST as ENTITY_BINDING_HTTP_POST

from cubicweb.server import DEBUG


def get_user(request):
    """ Retrieve posted user informations from database
    """
    if not request.POST or 'SAMLResponse' not in request.POST:
        return None

    config = request.registry['cubicweb.config']

    subject = retrieve_identity_from_client(config,
                                            request.POST['SAMLResponse'])
    if not subject:
        return None

    with request.registry['cubicweb.repository'].internal_cnx() as cnx:
        rset = cnx.execute('Any U WHERE U is CWUser, '
                           '            U login %(userid)s',
                           {'userid': subject.lower()})

    if not rset:
        return None

    return rset[0][0]


def get_metadata_from_uri(metadata_uri):
    """ Retrieve metadata xml content
    """

    if metadata_uri.startswith('file://'):
        with open(metadata_uri[7:], 'rb') as pipe:
            metadata = pipe.read()

        return metadata

    return requests_get(metadata_uri).text


def saml_client(config):
    """ Generate a SAML client from all-in-one.conf metadata
    """
    settings = {
        'debug': bool(DEBUG),
        'entityid': config['saml-entity-id'],
        'metadata': {
            'inline': [
                get_metadata_from_uri(config['saml-metadata-uri'])
            ],
        },
        'service': {
            'sp': {
                'endpoints': {
                    'assertion_consumer_service': [
                        (config['base-url'] + 'saml', BINDING_HTTP_POST),
                        (config['base-url'] + 'saml', BINDING_HTTP_REDIRECT),
                    ],
                },
                'allow_unsolicited':
                    config['saml-allow-unsolicited'],
                'authn_requests_signed':
                    config['saml-authn-requests-signed'],
                'logout_requests_signed':
                    config['saml-logout-requests-signed'],
                'want_assertions_signed':
                    config['saml-want-assertions-signed'],
                'want_response_signed':
                    config['saml-want-response-signed'],
            },
        },
    }

    configuration = Config()
    configuration.allow_unknown_attributes = True
    configuration.load(settings)

    return Saml2Client(config=configuration)


def retrieve_url_from_client(config, request):
    """ Generate SAML URL from metadata informations
    """
    reqid, info = saml_client(config).prepare_for_authenticate(
        relay_state=get_relay_state_from_request(config, request))

    # Select the IdP URL to send the AuthN request to
    return dict(info['headers']).get('Location', '')


def retrieve_identity_from_client(config, request):
    """ Retrieve identity from posted data
    """
    authn_response = saml_client(config).parse_authn_request_response(
        request, ENTITY_BINDING_HTTP_POST)

    if authn_response:
        authn_response.get_identity()

        subject = authn_response.get_subject()
        if subject:
            return subject.text


def get_relay_state_from_request(config, request):
    """ Generate relay state where the user should be returned after
    successfull login
    """
    if request.GET:
        return request.GET.get('postlogin_path', '')

    elif request.POST:
        url = request.POST.get('__errorurl', '')
        return url.replace(config['base-url'], '')

    return ''
