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


def includeme(config):
    """ Activate the SAML authenticate cube
    """
    from cubicweb_saml.pconfig import SAMLAuthenticationPolicy

    if config.registry.get('cubicweb.authpolicy') is None:
        raise ValueError("saml: the default cubicweb auth policy should be "
                         "available via the 'cubicweb.authpolicy' registry "
                         "config entry")

    cubicweb_config = config.registry['cubicweb.config']

    if not cubicweb_config.get('saml-metadata-uri', ''):
        raise KeyError(
            "saml: the option 'saml-metadata-uri' is empty or missing")

    if not cubicweb_config.get('saml-entity-id', ''):
        raise KeyError(
            "saml: the option 'saml-entity-id' is empty or missing")

    policy = SAMLAuthenticationPolicy(
        config.get_settings().get('cubicweb.auth.authtkt.session.secret'),
        config.get_settings().get('cubicweb.auth.authtkt.persistent.secret',
                                  'notsosecret'))

    config.registry['cubicweb.authpolicy']._policies.append(policy)

    config.add_route('saml', '/saml')
    config.scan('cubicweb_saml.pconfig')
