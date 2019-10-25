#
# Copyright (c) 2009, 2011, 2012, 2013, 2014
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
import pprint
import traceback
import textwrap
import base64
import xmlrpclib
import time
from uuid import uuid4
from xml.parsers import expat
from coils.net.foundation import PathObject
from coils.core import CoilsException
from coils.foundation import XMLRPC_callresponse, XMLRPC_faultresponse

ZOGI_PROTOCOL_LEVEL = '3A.0;-'

USE_ELEMENT_FLOW_SERIALIZATION = False

if not USE_ELEMENT_FLOW_SERIALIZATION:
    xmlrpc_result_serializer = xmlrpclib.dumps
    xmlrpc_fault_serialized = xmlrpclib.dumps
else:
    xmlrpc_result_serializer = XMLRPC_callresponse
    xmlrpc_fault_serialized = XMLRPC_faultresponse


class XMLRPCServer(PathObject):

    name = 'xmlrpc'

    def __init__(self, parent, bundles, **params):
        PathObject.__init__(self, parent, **params)
        self.bundles = bundles

    def do_GET(self):
        raise CoilsException('XML-RPC calls must be POST commands')

    def do_POST(self):

        # Create a unique identified for this call
        callid = uuid4().hex

        '''Deserialize Request'''
        result = None
        start_time = time.time()
        payload = None

        try:

            payload = self.request.get_request_payload()
            rpc = xmlrpclib.loads(payload, use_datetime=True)

        except xmlrpclib.ResponseError as exc:
            """
            ResponseError - the XML request cannot be understood.
            """
            self.log.exception(exc)
            data = base64.encodestring(payload)
            tw = textwrap.TextWrapper(width=76)
            self.context.send_administrative_notice(
                subject='XML-RPC Request Cannot Be Parsed',
                message=(
                    'Context: {0} [{1}]\n'
                    'Request:\n'
                    '{2}\n\n'
                    'Traceback:\n'
                    '{3}\n'
                    .format(
                        self.context.account_id,
                        self.context.login,
                        tw.fill(data),
                        traceback.format_exc()
                    )
                )  # end message=
            )  # end send_administrative_notice
            raise exc

        except expat.ExpatError as exc:
            """
            ExpatError - the request is not valid XML
            """
            self.log.exception(exc)
            if payload:
                data = base64.encodestring(payload)
                tw = textwrap.TextWrapper(width=76)
                self.context.send_administrative_notice(
                    subject='XML-RPC Request is not valid XML (Expat Error)',
                    message=(
                        'Context: {0} [{1}]\n'
                        'Request:\n'
                        '{2}\n\n'
                        'Traceback:\n'
                        '{3}\n'
                        .format(
                            self.context.account_id,
                            self.context.login,
                            tw.fill(data),
                            traceback.format_exc()
                        )
                    )  # end message=
                )  # end send_administrative_notice
                tw = None
                data = None
            raise exc

        except Exception as exc:
            """
            Generic exception handler for deserializing a request, this will
            end up as an uninformative Server HTTP/500 error.
            """
            self.log.exception(exc)
            raise exc

        """Perform Request"""

        namespace = None
        method_name = None
        parameters = None
        result_status = 'undefined'
        result_message = 'undefined'
        result_errors = 0

        try:
            method = rpc[1].split('.')

            if (len(method) < 2):
                raise CoilsException('XML-RPC request without namespace.')
            if (len(method) > 2):
                raise CoilsException('XML-RPC with convoluted namespace.')

            namespace = method[0]
            method_name = method[1]
            parameters = rpc[0]

            # start a record of the call in the RPC2 log
            self.context.send(
                None,
                'coils.administrator/rpc2_log',
                {
                    'callid': callid,
                    'login': self.context.login,
                    'method': '{0}.{1}'.format(namespace, method_name, ),
                    'params': parameters,
                },
            )

            for bundle in self.bundles:
                """
                Find the first bundle we have that provides this RPC namespace.
                """
                if (bundle.__namespace__ == namespace):
                    handler = bundle(self.context)
                    try:
                        call = getattr(handler, method_name)
                    except Exception:
                        raise CoilsException(
                            'Namespace "{0}" has no such method as "{1}"'.
                            format(namespace, method_name))
                        break
                    else:
                        result = apply(call, parameters)
                        break
            else:
                raise CoilsException(
                    'No such API namespace as "{0}"'.format(namespace, )
                )

        except Exception as exc:

            result_status = 'error'
            result_message = str(exc)
            result_errors += 1

            self.log.error(
                'XML-RPC Method Perform Exception; method={0}.{1}({2})'.
                format(
                    namespace,
                    method_name,
                    parameters,
                )
            )
            self.log.exception(exc)

            if self.context.amq_available:

                self.context.send_administrative_notice(
                    subject='XML-RPC Method Perform Exception',
                    message=('Method: {0}.{1}\n'
                             'Context: {2} [{3}]\n'
                             'Parameters: {4}\n'
                             'Traceback: {5}\n'.
                             format(namespace,
                                    method_name,
                                    self.context.account_id,
                                    self.context.login,
                                    pprint.pformat(parameters),
                                    traceback.format_exc()
                                    )),
                    urgency=5,
                    category='xmlrpc-proxy',
                    attachments=[])

            raise exc

        else:
            # Call completed without exception
            result_status = 'complete'
            result_message = '{0}'.format(type(result), )
            result_errors = 0

        finally:
            duration = time.time() - start_time
            self.log.debug('XML-RPC processing complete')

            # Notify the RPC2 log about the completion of the call
            self.context.send(
                None,
                'coils.administrator/rpc2_log',
                {
                    'callid': callid,
                    'status': result_status,
                    'result': result_message,
                    'duration': duration,
                    'errors': result_errors,
                },
            )

        """Serialize Response"""

        if result is not None:
            try:
                if self.context.user_agent_description['xmlrpc']['allowNone']:
                    result = xmlrpc_result_serializer(
                        tuple([result, ]),
                        allow_none=True,
                        methodresponse=True,
                    )
                else:
                    result = xmlrpc_result_serializer(
                        tuple([result, ]),
                        methodresponse=True,
                    )
            except Exception as exc:
                self.log.error('XML-RPC Serialization Error')
                self.log.exception(exc)
                self.context.send_administrative_notice(
                    subject='XML-RPC Serialization Error',
                    message=(
                        'Method: {0}.{1}\n'
                        'Parameters: {2}\n'
                        'Context: {3} [{4}]\n'
                        'Representation: {5}\n\n'
                        'Traceback: {6}\n'.
                        format(
                            namespace,
                            method_name,
                            pprint.pformat(parameters),
                            self.context.account_id,
                            self.context.login,
                            pprint.pformat(result),
                            traceback.format_exc(),
                        )
                    ),
                    urgency=5,
                    category='xmlrpc-proxy',
                    attachments=[],
                )
                raise exc

        if self.context.user_agent_description['omphalos']['associativeLists']:
            associative_lists = 't'
        else:
            associative_lists = 'f'

        self.request.simple_response(
            200,
            data=result,
            mimetype='text/xml',
            headers={
                'X-COILS-ZOGI-PROTOCOL-LEVEL': ZOGI_PROTOCOL_LEVEL,
                'X-COILS-ASSOCIATIVE-LISTS': associative_lists,
                'X-COILS-SESSION-ID': self.context.session_id,
            }
        )
        return
