# copyright 2010-2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-trustedauth application package

authentication plugin for cubicweb instances behind a trusted
reverse proxy managing authentication  (eg. apache + kerberos)
"""


def includeme(config):
    """Activate the trusted authentication policy in a
    pyramid_cubiweb instance.

    Usually called from the main pyramid_cubicweb.core configurator
    (see ``pyramid_cubicweb.core``).

    See also :ref:`defaults_module`

    """
    from cubicweb_trustedauth.pconfig import TrustedAuthenticationPolicy
    policy = TrustedAuthenticationPolicy()

    # # add some bw compat methods
    # # these ease code factorization between pyramid related code and legacy one
    # config.add_request_method(
    #     lambda req, header, default=None: req.headers.get(header, default),
    #     name='get_header', property=False, reify=False)
    # config.add_request_method(lambda req: req.method,
    #     name='http_method', property=False, reify=False)

    if config.registry.get('cubicweb.authpolicy') is None:
        err = "trustedauth: the default cubicweb auth policy should be "\
              "available via the 'cubicweb.authpolicy' registry config "\
              "entry"
        raise ValueError(err)

    # if we use (the default) a multiauth policy in CW, append
    # signedrequest to it
    mainpolicy = config.registry['cubicweb.authpolicy']
    mainpolicy._policies.append(policy)
