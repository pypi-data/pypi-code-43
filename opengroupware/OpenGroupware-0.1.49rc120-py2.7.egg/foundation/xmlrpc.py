# Copyright (c) 2010, 2013, 2014
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

from datetime import datetime, date
from api import elementflow


class XMLRPCException(Exception):
    pass


class XMLRPCDataTypeException(XMLRPCException):
    pass


class XMLRPCNULLValueWithoutAgentSupport(XMLRPCException):
    pass


try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO


def XMLRPC_methodcall(method_name, arguments, ):
    pass


'''
   TODO: Render dates, & datetimes
   TODO: support supports_null flag
'''


def XMLRPC_faultresponse(
    params,
    methodname=None,
    methodresponse=True,
    encoding='utf-8',
    allow_null=False,
    fallback_serializer=None,
):
    """
    Format an XML-RPC fault response.  The methodresponse parameter is not
    used, it is only provided to maintain compatibility with the contract
    established by the xmlrpclib module in the standard library.  The python
    standard library provides xmlrpclib.dumps to handle both complete call
    results and exception results as Fault responses; we separate fault and
    complete responses into two functions.
    """

    exception = params

    # Find faultString
    if not hasattr(exception, 'faultString'):
        fault_string = exception.message
    else:
        fault_string = exception.faultString

    # Find faultCode

    if not hasattr(exception, 'faultCode', ):
        fault_code = 0
    else:
        fault_code = exception.faultCode

    # Serialize Response
    stream = StringIO()
    with elementflow.xml(stream, u'methodresponse') as response:
        with response.container('fault'):
            with response.container('value'):
                with response.container('value'):
                    with response.container('struct'):
                        with response.container('struct'):
                            with response.container('member'):
                                response.element('name', text='faultCode')
                                with response.container('value'):
                                    response.element(
                                        'int', text=str(fault_code)
                                    )
                            with response.container('member'):
                                response.element('name', text='faultString')
                                with response.container('value'):
                                    response.element(
                                        'string',
                                        text=str(fault_string),
                                    )
    stream.seek(0)
    return stream


def XMLRPC_callresponse(
    params,
    methodname=None,
    methodresponse=True,
    encoding='utf-8',
    allow_null=False,
    fallback_serializer=None,
):
    """
    Serialize an XML-RPC calls response when call completed successfully.
    The methodresponse and methodname parameters are not used, they are only
    provided to maintain compatibility with the contract established by the
    xmlrpclib module in the standard library.  The python standard library
    provides xmlrpclib.dumps to handle both complete call results and
    exception results as Fault responses; we separate fault and complete
    responses into two functions.
    """

    def render_value(xml, value, ):
        if isinstance(value, basestring, ):
            xml.element(
                'string',
                text=value,
            )
        elif isinstance(value, int) or isinstance(value, long):
            xml.element(
                'int',
                text=str(value),
            )
        elif isinstance(value, float):
            xml.element(
                'double',
                text=str(value),
            )
        elif isinstance(value, list):
            with xml.container('array'):
                for item in value:
                    with xml.container('value'):
                        render_value(xml, item)
        elif isinstance(value, dict):
            with xml.container('struct'):
                for key, value in value.items():
                    with xml.container('member'):
                        xml.element('name', text=str(key))
                        with xml.container('value'):
                            render_value(xml, value, )
        elif isinstance(value, datetime):
            xml.element(
                'dateTime.iso8601',
                text=datetime.strftime('%Y%m%dT%H:%M:%S'),
            )
        elif isinstance(value, date):
            xml.element(
                'dateTime.iso8601',
                datetime.strftime('%Y%m%dT%00:00:00'),
            )
        elif value is None:
            if allow_null:
                xml.element('nil', )
            else:
                raise XMLRPCNULLValueWithoutAgentSupport(
                    'Cannot serialize NULL value for the current user-agent'
                )
        elif fallback_serializer:
            fallback_serializer(xml, value)
        else:
            raise XMLRPCDataTypeException(
                'Cannot serialize type "{0}" in XML-RPC response'.
                format(type(value), )
            )

    stream = StringIO()
    with elementflow.xml(stream, u'methodresponse') as xml:
        with xml.container('params'):
            with xml.container('param'):
                with xml.container('value'):
                    render_value(xml, params, )
    stream.seek(0)
    return stream
