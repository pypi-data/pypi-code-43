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

options = (
    ('saml-metadata-uri', {
        'type': 'string',
        'default': '',
        'help': 'SAML v2 metadata uri which can be read from a file '
                '(file://<absolute_path>) or retrieved from a specific URL'
                '(http[s]://...)',
        'group': 'saml',
        'level': 5,
    }),
    ('saml-entity-id', {
        'type': 'string',
        'default': '',
        'help': 'The globally unique identifier of the entity.',
        'group': 'saml',
        'level': 5,
    }),
    ('saml-allow-unsolicited', {
        'type': 'yn',
        'default': True,
        'help': "Don't verify that the incoming requests originate from us "
                "via the built-in cache for authn request ids in pysaml2",
        'group': 'saml',
        'level': 5,
    }),
    ('saml-authn-requests-signed', {
        'type': 'yn',
        'default': False,
        'help': "Indicates if the Authentication Requests sent by this SP "
                "should be signed by default.",
        'group': 'saml',
        'level': 5,
    }),
    ('saml-logout-requests-signed', {
        'type': 'yn',
        'default': True,
        'help': "Indicates if this entity will sign the Logout Requests "
                "originated from it.",
        'group': 'saml',
        'level': 5,
    }),
    ('saml-want-assertions-signed', {
        'type': 'yn',
        'default': True,
        'help': "Indicates if this SP wants the IdP to send the assertions "
                "signed. This sets the WantAssertionsSigned attribute of the "
                "SPSSODescriptor node of the metadata so the IdP will know "
                "this SP preference.",
        'group': 'saml',
        'level': 5,
    }),
    ('saml-want-response-signed', {
        'type': 'yn',
        'default': False,
        'help': "Indicates that Authentication Responses to this SP must be "
                "signed. If set to True, the SP will not consume any SAML "
                "Responses that are not signed.",
        'group': 'saml',
        'level': 5,
    }),
)
