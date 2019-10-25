#
# Copyright (c) 2017
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
from coils.core import CoilsException, NotImplementedException
from coils.foundation import ldap_paged_search, LDAPConnectionFactory
from coils.core.logic import ActionCommand
from dsml1_writer import DSML1Writer

try:
    import ldap
    from ldif import ParseLDIF
    import ldap.modlist as modlist
except:
    class LDAPAddAction(object):
        pass
else:
    class LDAPAddAction(ActionCommand):
        __domain__ = "action"
        __operation__ = "ldap-add"
        __aliases__ = ['ldapAddAction', "ldapAdd", ]

        def __init__(self):
            ActionCommand.__init__(self)

        @property
        def result_mimetype(self):
            return 'text/plain'

        def do_action(self):

            """
            payload data must be parsed into; this is the natural form from
            parsing an LDIF
            [(DN, {attributes: values}, ),]
            """

            if self.input_mimetype in ('text/plain', 'text/x-ldif'):
                # a text file is assumed to be LDIF
                parsed_data = ParseLDIF(self.rfile)
                dn, attributes = parsed_data[0]
                print dn
            elif self.input_mimetype in ('application/json', 'text/x-json', ):
                # TODO: implement LDAP from JSON
                raise NotImplementedException(
                    'Create LDAP object from JSON not yet implemented; '
                    'patches welcome!'
                )
            elif self.input_mimetype in ('application/xml', 'text/xml', ):
                # TODO: implement LDAP from XML (assuming DSML)
                raise NotImplementedException(
                    'Create LDAP object from XML(DSML) not yet implemented; '
                    'patches welcome!'
                )
            else:
                raise CoilsException(
                    'Unknown mime-type "{0}"'.format(self.input_mimetype, )
                )

            dsa = LDAPConnectionFactory.Connect(self._dsa)

            created_dns = list()

            # create each object from the parsed data, record the DN
            # of each object created as we will in turn retrieve the
            # new object from the DSA
            for obj in parsed_data:
                dn, attributes = obj
                ldif = modlist.addModlist(attributes)

                if dsa:
                    dsa.add_s(dn, ldif)
                    created_dns.append(dn)
                    self.log_message(
                        'Created DN:{0}'.format(dn, ), category='info'
                    )

            self.log_message(
                '{0} objects created'.format(len(created_dns), ),
                category='info',
            )

            if not self._xroot:
                # if no root is specified we write no output
                return

            # retrieve the objects we created
            results = list()
            for created_dn in created_dns:
                try:
                    result = ldap_paged_search(
                        connection=dsa,
                        logger=self.log,
                        search_filter='(objectclass=*)',
                        search_base=created_dn,
                        attributes=['*'],
                        search_scope=ldap.SCOPE_BASE,
                        search_limit=1,
                    )
                except ldap.NO_SUCH_OBJECT as exc:
                    self.log.info(
                        'LDAP NO_SUCH_OBJECT exception for DN:{0}'.
                        format(created_dn, )
                    )
                except ldap.INSUFFICIENT_ACCESS as exc:
                    self.log.exception(exc)
                    self.log.info(
                        'LDAP INSUFFICIENT_ACCESS exception, generating '
                        'empty message'
                    )
                    self.log_message(
                        'INSUFFICIENT_ACCESS exception retrieving DN:{0}'.
                        format(created_dn, ),
                        category='error',
                    )
                except ldap.SERVER_DOWN as exc:
                    self.log.exception(exc)
                    self.log.warn('Unable to contact LDAP server!')
                    raise exc
                except Exception as exc:
                    self.log.error('Exception in action ldapSearch')
                    self.log.exception(exc)
                    raise exc
                else:
                    results.extend(result)
                    self.log_message(
                        'retrieved DN:{0}'.format(result[0][0], ),
                        category='info',
                    )
                    results.append(result)

            # write the objects we created as DSML
            if (self.debugOn):
                self.log.debug(
                    'LDAP SEARCH: Formatting results to DSML.'
                )
            writer = DSML1Writer()
            writer.write(results, self.wfile)

            dsa.unbind()

        def parse_action_parameters(self):
                self._dsa = self.action_parameters.get('dsaName', None)
