# Copyright (c) 2009, 2013, 2015, 2017
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import re
from authenticator import Authenticator
from coils.foundation import ServerDefaultsManager


LDAP_INVALID_CREDENTIALS = 100
LDAP_DENIED_DUE_TO_TIME = 101
LDAP_DENIED_DUE_TO_SOURCE = 102
LDAP_PASSWORD_EXPIRED = 103
LDAP_ACCOUNT_DISABLED = 104
LDAP_ACCOUNT_EXPIRED = 105
LDAP_PASSWORD_CHANGE_REQUIRED = 106
LDAP_ACCOUNT_LOCKED = 107
LDAP_GENERIC_FAILURE = 108


LDAP_MESSAGE_TEXT = {
    LDAP_INVALID_CREDENTIALS: 'invalid credentials',
    LDAP_DENIED_DUE_TO_TIME: 'DSA denied access at this time',
    LDAP_DENIED_DUE_TO_SOURCE: 'DSA denied access from this source',
    LDAP_PASSWORD_EXPIRED: 'account password has expired',
    LDAP_ACCOUNT_DISABLED: 'account is currently disabled',
    LDAP_ACCOUNT_EXPIRED: 'account is expired',
    LDAP_PASSWORD_CHANGE_REQUIRED: 'password change is required',
    LDAP_ACCOUNT_LOCKED: 'account is currently locked',
    LDAP_GENERIC_FAILURE: 'generic LDAP authentication failure',
}


AD_INVALID_EXCEPTION_PATTERN = r'''^80090308: LdapErr: (?P<errorid>[A-z0-9\-]*?), comment: (?P<comment>[A-z0-9\ ]*?), data (?P<data>[a-z0-9]*?),'''  # noqa


AD_TO_OGO_DATA_TRANSFORM = {
    '530': LDAP_DENIED_DUE_TO_TIME,
    '531': LDAP_DENIED_DUE_TO_SOURCE,
    '532': LDAP_PASSWORD_EXPIRED,
    '533': LDAP_ACCOUNT_DISABLED,
    '701': LDAP_ACCOUNT_EXPIRED,
    '773': LDAP_PASSWORD_CHANGE_REQUIRED,
    '775': LDAP_ACCOUNT_LOCKED,
}


def parse_invalid_credentials_exception(exc):
    code = LDAP_INVALID_CREDENTIALS
    try:
        info_string = exc.args[0].get('info', None)
        if info_string:
            if info_string.startswith('80090308: LdapErr:'):
                # Active Directory!
                pattern = re.compile(AD_INVALID_EXCEPTION_PATTERN)
                match = re.match(pattern, info_string)
                if match:
                    args = match.groupdict()
                    code = AD_TO_OGO_DATA_TRANSFORM.get(
                        args['data'], LDAP_INVALID_CREDENTIALS,
                    )

    except:
        pass
    return code, LDAP_MESSAGE_TEXT.get(code, 'unknown authentication failure')

LDAP_OPT_OFF = 0

try:
    import ldap
    import ldap.sasl
    if 'OPT_OFF' in dir(ldap):
        """
        HACK: work around some older versions of python-ldap which do not
        define ldap.OPT_OFF; for example version 0.4.9.6
        """
        LDAP_OPT_OFF = ldap.OPT_OFF
    if 'OPT_REFERRALS' not in dir(ldap):
        raise Exception('Antique version of python-ldap ignored')
except:
    class LDAPAuthenticator(Authenticator):
        def __init__(self, metadata, options):
            raise Exception('LDAP support not available')
else:
    import ldaphelper

    class LDAPAuthenticator(Authenticator):
        _dsa = None
        _ldap_debug = None

        def __init__(self,  metadata, options, password_cache=None):
            self._verify_options(options)
            Authenticator.__init__(
                self, metadata, options, password_cache=password_cache,
            )

        @property
        def ldap_debug_enabled(self):
            if (LDAPAuthenticator._ldap_debug is None):
                if (
                    ServerDefaultsManager()
                    .bool_for_default('LDAPDebugEnabled')
                ):
                    LDAPAuthenticator._ldap_debug = True
                else:
                    LDAPAuthenticator._ldap_debug = False
            return LDAPAuthenticator._ldap_debug

        def _verify_options(self, options):
            # TODO: Check the options to make sure we have function values
            return

        def _bind_and_search(self, options, login):
            # Bind to the DSA and search for the user's DN
            dsa = ldap.initialize(options['url'])
            ldap.set_option(ldap.OPT_REFERRALS, LDAP_OPT_OFF)
            if (options['start_tls'] == 'YES'):
                if (self.ldap_debug_enabled):
                    self.log.debug('Starting TLS')
                dsa.start_tls_s()
            if (options['binding'] == 'SIMPLE'):
                dsa.simple_bind_s(options['bind_identity'],
                                  options['bind_secret'])
                if (self.ldap_debug_enabled):
                    self.log.debug('Starting TLS')
            elif (options['binding'] == 'DIGEST'):
                tokens = ldap.sasl.digest_md5(options['bind_identity'],
                                              options['bind_secret'])
                dsa.sasl_interactive_bind_s("", tokens)
                self._search_bind()
            search_filter = options["search_filter"]
            if (search_filter is None):
                search_filter = '({0}={1})'.format(
                    options["uid_attribute"], login,
                )
                if (self.ldap_debug_enabled):
                    self.log.error(
                        'No LDAP filter configured, defaulting to "{0}"'
                        .format(search_filter, )
                    )
            else:
                search_filter = search_filter % login
            if (self.ldap_debug_enabled):
                self.log.debug(
                    'LDAP Container: {0}'.format(options["search_container"])
                )
                self.log.debug(
                    'LDAP Filter: {0}'.format(search_filter, )
                )
                self.log.debug(
                    'LDAP UID Attribute: {0}'
                    .format(options["uid_attribute"], )
                )
            result = dsa.search_s(
                options["search_container"],
                ldap.SCOPE_SUBTREE,
                search_filter,
                [options["uid_attribute"], ]
            )
            result = ldaphelper.get_search_results(result)
            if (self.ldap_debug_enabled):
                self.log.debug('Found {0} results.'.format(len(result)))
            return result

        def _test_simple_bind(self, options, dn, secret):
            if not secret.strip():
                self.log.info(
                    'Attempt to authenticated as "{0}" '
                    'with empty password denied'
                    .format(dn, )
                )
                return False
            dsa = ldap.initialize(options['url'])
            ldap.set_option(ldap.OPT_REFERRALS, LDAP_OPT_OFF)
            if (options['start_tls'] == 'YES'):
                LDAPAuthenticator._dsa.start_tls_s()
            result = False
            try:
                dsa.simple_bind_s(dn, secret)
                result = True
                dsa.unbind()
            except ldap.INVALID_CREDENTIALS as exc:
                self.log.exception(exc)
                code, text = parse_invalid_credentials_exception(exc)
                self.set_response_detail(code, text)
            except Exception as exc:
                self.log.exception(exc)
                self.set_response_detail(
                    LDAP_GENERIC_FAILURE,
                    LDAP_MESSAGE_TEXT[LDAP_GENERIC_FAILURE],
                )
            return result

        def _get_ldap_object(self):

            if not self.login:
                self.log.warn(
                    'Request for empty UID; not login string provided.'
                )
                self.raise_authentication_exception(
                    'Request for empty UID; not login string provided.'
                )

            if (self.options['binding'] == 'SIMPLE'):
                accounts = self._bind_and_search(self.options, self.login)
                if (len(accounts) == 0):
                    self.raise_authentication_exception(
                        'Matching account not returned by DSA'
                    )
                elif (len(accounts) > 1):
                    accounts = [accounts[0], ]  # HACK
                    """
                    raise AuthenticationException(
                        'Dupllicate accounts returned by DSA'
                    )
                    """
                # Only one found
                dn = accounts[0].get_dn()
                if (self.ldap_debug_enabled):
                    self.log.debug(
                        'Testing authentication bind as {0}'.format(dn, )
                    )
                if (dn is None):
                    self.log.warn('LDAP object with null DN!')
                if (self._test_simple_bind(self.options, dn, self.secret)):
                    self.log.debug('LDAP bind with {0}'.format(dn))
                    return accounts[0]
                else:
                    self.raise_authentication_exception(
                        'DSA declined username or password'
                    )
            elif (self.options['binding'] == 'SASL'):
                # TODO Implement LDAP SASL bind test
                self.raise_authentication_exception(
                    'SASL bind test not implemented!'
                )

        def authenticate(self):
            if (Authenticator.authenticate(self)):
                return True

            if self.check_cached_credentials(self.login, self.secret, ):
                if (self.debugging_enabled):
                    self.log.debug(
                        'Password verified from cached credentials; '
                        'access granted'
                    )
                return True

            try:
                ldap_object = self._get_ldap_object()
                if (ldap_object is not None):
                    if self.debugging_enabled:
                        self.log.debug(
                            'Password verified against LDAP DSA database; '
                            'access granted'
                        )
                    self.cache_successful_credentials(
                        self.login, self.secret,
                    )
                    return True
            except Exception as exc:
                self.log.error('Error processing LDAP authentication request')
                self.log.exception(exc)
                self.revoke_cached_credentials(self.login)

            self.raise_authentication_exception(
                'Incorrect username or password'
            )

        def provision_login(self):
            '''
            Authenticators can override this method to support auto-
            provisioning of user accounts.  If the account cannot be
            auto-provsioned this method should return None; if the
            authenticator does not support provisioning just return None.
            '''
            # ldap_object = self._get_ldap_object()
            return None
