'''
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
'''

import ssl
import socket
import http.client
import cgi
import os
import time
import sys

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn, BaseServer
from http import HTTPStatus

import microserver.glb as glb
from microserver.hookset import HookSet


def verbose_print(*args, **kwargs):
    """
    Print output if verbosity is set.

    args and kwargs should be the paramenters that would be passed to Python's
    builtin print().
    """
    if glb.verbose:
        print(*args, **kwargs)


class ThreadingServer(ThreadingMixIn, HTTPServer):
    '''This class forces the creation of a new thread on each connection'''

    def __init__(self, local_addr, handler_class, hooks=None):
        HTTPServer.__init__(self, local_addr, handler_class)
        self.hook_set = HookSet()
        if (hooks):
            self.hook_set.load(hooks)


class SSLServer(ThreadingMixIn, HTTPServer):
    def __init__(self, server_address, HandlerClass, key, cert, clientCA, hooks=None, clientverify=False):
        BaseServer.__init__(self, server_address, HandlerClass)
        self.hook_set = HookSet()

        self.daemon_threads = True
        self.protocol_version = 'HTTP/1.1'

        if hooks:
            self.hook_set.load(hooks)

        if clientverify:
            self.socket = ssl.wrap_socket(socket.socket(self.address_family, self.socket_type),
                                          keyfile=key, certfile=cert, server_side=True, cert_reqs=ssl.CERT_REQUIRED, ca_certs=clientCA)
        else:
            self.socket = ssl.wrap_socket(socket.socket(self.address_family, self.socket_type),
                                          keyfile=key, certfile=cert, server_side=True)

        self.server_bind()
        self.server_activate()


class MyHandler(BaseHTTPRequestHandler):
    def handleExpect100Continue(self, contentLength, chunked=False):
        print("....expect", contentLength)
        self.wfile.write(bytes('HTTP/1.1 100 Continue\r\n\r\n', 'UTF-8'))
        if(not chunked):
            message = self.rfile.read(contentLength)
        else:
            readChunks()

    # intentionally overriding to redirect custom methods to do_GET/POST methods
    def handle_one_request(self):
        METHODS_UNDER_GET = ['GET', 'OPTIONS', 'PROPFIND', 'DELETE', 'REPORT']
        METHODS_UNDER_POST = ['POST', 'PROPPATCH', 'PUT']
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                return
            if not self.raw_requestline:
                self.close_connection = True
                return
            if not self.parse_request():
                # An error code has been sent, just exit
                return
            if self.command in METHODS_UNDER_GET:
                mname = 'do_' + 'GET'
            elif self.command in METHODS_UNDER_POST:
                mname = 'do_' + 'POST'
            else:
                mname = 'do_' + self.command
            if not hasattr(self, mname):
                self.send_error(
                    HTTPStatus.NOT_IMPLEMENTED,
                    "Unsupported method (%r)" % self.command)
                return
            method = getattr(self, mname)
            method()
            # actually send the response if not already done.
            self.wfile.flush()
        except socket.timeout as e:
            # a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.close_connection = True
            return

    def getLookupKey(self, requestline):
        kpath = ""
        path = ""
        url_part = requestline.split(" ")
        if url_part:
            path = url_part[1]
        argsList = []
        keyslist = glb.lookupKey.split("}")
        for keystr in keyslist:
            if keystr == '{PATH':
                kpath = kpath + path
                continue  # do not include path in the list of header fields
            if keystr == '{HOST':
                # assuming we are always gonna get stuff from ATS, which strips the host from url
                kpath = kpath + self.headers.get('Host')
                continue
            if keystr == '{URL':
                kpath = kpath + request.getURL()
                continue
            stringk = keystr.replace("{%", "")
            argsList.append(stringk)
        KeyList = []
        for argsL in argsList:
            if len(argsL) > 0:
                val = self.headers.get(argsL)
                if val:
                    field_val, __ = cgi.parse_header(val)
                else:
                    field_val = None
                if field_val != None:
                    KeyList.append(field_val)
        key = "".join(KeyList) + kpath

        return key

    def get_response_code(self, header):
        # this could totally go wrong
        return int(header.split(' ')[1])

    def generator(self):
        yield 'micro'
        yield 'server'
        yield 'apache'
        yield 'traffic'
        yield 'server'

    def send_response(self, code, message=None):
        ''' Override `send_response()`'s tacking on of server and date header lines. '''
        self.send_response_only(code, message)

    def createDummyBodywithLength(self, numberOfbytes):
        if numberOfbytes == 0:
            return None
        body = 'a'
        body += 'b' * (numberOfbytes - 1)
        return body

    def writeChunkedData(self):
        for chunk in self.generator():
            response_string = bytes('%X\r\n%s\r\n' %
                                    (len(chunk), chunk), 'UTF-8')
            self.wfile.write(response_string)
        response_string = bytes('0\r\n\r\n', 'UTF-8')
        self.wfile.write(response_string)

    def readChunks(self):
        raw_data = b''
        raw_size = self.rfile.readline(65537)
        size = str(raw_size, 'UTF-8').rstrip('\r\n')
        # print("==========================================>",size)
        size = int(size, 16)
        while size > 0:
            chunk = self.rfile.read(size + 2)  # 2 for reading /r/n
            raw_data += chunk
            raw_size = self.rfile.readline(65537)
            size = str(raw_size, 'UTF-8').rstrip('\r\n')
            size = int(size, 16)
        # read the extra blank newline \r\n after the last chunk
        chunk = self.rfile.readline(65537)

    def send_header(self, keyword, value):
        """Send a MIME header to the headers buffer."""
        if self.request_version != 'HTTP/0.9':
            if not hasattr(self, '_headers_buffer'):
                self._headers_buffer = []
            self._headers_buffer.append(
                ("%s: %s\r\n" % (keyword, value)).encode('UTF-8', 'strict'))  # original code used latin-1.. seriously?

        if keyword.lower() == 'connection':
            if value.lower() == 'close':
                self.close_connection = True
            elif value.lower() == 'keep-alive':
                self.close_connection = False

    def parse_request(self):
        """Parse a request (internal).

        The request should be stored in self.raw_requestline; the results
        are in self.command, self.path, self.request_version and
        self.headers. Any matching response is in self.response.

        Return True for success, False for failure; on failure, an
        error is sent back.

        """

        self.command = None  # set in case of error on the first line
        self.request_version = version = self.default_request_version
        self.close_connection = True
        requestline = str(self.raw_requestline, 'UTF-8')
        requestline = requestline.rstrip('\r\n')
        self.requestline = requestline

        # Examine the headers and look for a Connection directive.
        try:
            self.headers = http.client.parse_headers(self.rfile,
                                                     _class=self.MessageClass)
            key = self.getLookupKey(self.requestline)
            self.respLookupKey = key
            self.resp = glb.replayDict[key] if key in glb.replayDict else None
            resp_options = None

            if self.resp:
                resp_options = self.resp.getOptions()

            # if self.resp is None:
            if not resp_options or 'skipHooks' not in resp_options:
                verbose_print("Invoking read request hook")
                self.server.hook_set.invoke(
                    HookSet.ReadRequestHook, self.headers)
            # read message body
            if self.headers.get('Content-Length') != None:
                bodysize = int(self.headers.get('Content-Length'))
                message = self.rfile.read(bodysize)
            elif self.headers.get('Transfer-Encoding', "") == 'chunked':
                self.readChunks()
        except http.client.LineTooLong:
            self.send_error(
                HTTPStatus.BAD_REQUEST,
                "Line too long")
            return False
        except http.client.HTTPException as err:
            self.send_error(
                HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE,
                "Too many headers",
                str(err)
            )
            return False

        words = requestline.split()
        if len(words) == 3:
            command, path, version = words
            if version[:5] != 'HTTP/':
                self.send_error(
                    HTTPStatus.BAD_REQUEST,
                    "Bad request version (%r)" % version)
                return False
            try:
                base_version_number = version.split('/', 1)[1]
                version_number = base_version_number.split(".")
                # RFC 2145 section 3.1 says there can be only one "." and
                #   - major and minor numbers MUST be treated as
                #      separate integers;
                #   - HTTP/2.4 is a lower version than HTTP/2.13, which in
                #      turn is lower than HTTP/12.3;
                #   - Leading zeros MUST be ignored by recipients.
                if len(version_number) != 2:
                    raise ValueError
                version_number = int(version_number[0]), int(version_number[1])
            except (ValueError, IndexError):
                self.send_error(
                    HTTPStatus.BAD_REQUEST,
                    "Bad request version (%r)" % version)
                return False
            if version_number >= (1, 1) and self.protocol_version >= "HTTP/1.1":
                self.close_connection = False
            if version_number >= (2, 0):
                self.send_error(
                    HTTPStatus.HTTP_VERSION_NOT_SUPPORTED,
                    "Invalid HTTP Version (%s)" % base_version_number)
                return False
        elif len(words) == 2:
            command, path = words
            self.close_connection = True
            if command != 'GET':
                self.send_error(
                    HTTPStatus.BAD_REQUEST,
                    "Bad HTTP/0.9 request type (%r)" % command)
                return False
        elif not words:
            print("bla bla on 157 => {1}".format(self.close_connection))
            return False
        else:
            self.send_error(
                HTTPStatus.BAD_REQUEST,
                "Bad request syntax (%r)" % requestline)
            return False
        self.command, self.path, self.request_version = command, path, version

        conntype = self.headers.get('Connection', "")
        if conntype.lower() == 'close':
            self.close_connection = True
        elif (conntype.lower() == 'keep-alive' and
              self.protocol_version >= "HTTP/1.1"):
            self.close_connection = False

        return True

    def do_GET(self):
        if glb.timeDelay and self.requestline != "GET /ruok HTTP/1.1":
            time.sleep(glb.timeDelay)

        try:
            response_string = None
            chunkedResponse = False
            if self.resp is None:
                self.send_response(404)
                self.send_header('Server', 'MicroServer')
                self.send_header('Connection', 'close')
                self.end_headers()
                return
            else:
                verbose_print("Serving GET {0}...".format(
                    self.respLookupKey), end=' ')
                headers = self.resp.getHeaders()

                # set status codes
                status_code = self.resp.getStatus()
                self.send_response(status_code)

                # set headers
                for header in headers:
                    if 'Content-Length' == header:
                        length = headers[header]  # headers['Content-Length']
                        self.send_header('Content-Length', str(length))
                        response_string = self.createDummyBodywithLength(
                            int(length))
                        continue
                    if 'Transfer-Encoding' == header:
                        self.send_header('Transfer-Encoding', 'Chunked')
                        response_string = '%X\r\n%s\r\n' % (len('ats'), 'ats')
                        chunkedResponse = True
                        continue

                    self.send_header(header, headers[header])

                # TODO: temp fix, real fix should be in traffic dump or sanitizer
                if (chunkedResponse):
                    pass
                elif response_string != None and response_string != '':
                    pass
                elif self.resp.getContentSize():
                    print("injecting content-length header..", end=' ')
                    self.send_header('Content-Length',
                                     str(self.resp.getContentSize()))

                self.end_headers()

                if self.resp.getBody():
                    response_string = self.resp.getBody()

                if chunkedResponse:
                    self.writeChunkedData()
                elif response_string != None and response_string != '':
                    self.wfile.write(bytes(response_string, 'UTF-8'))
                elif self.resp.getContentSize():
                    self.wfile.write(bytes(self.createDummyBodywithLength(
                        int(self.resp.getContentSize())), 'UTF-8'))

                verbose_print("Finished")
        except:
            e = sys.exc_info()
            print("Error in GET handling {0}".format(self.respLookupKey), e)
            self.send_response(400)
            self.send_header('Connection', 'close')
            self.end_headers()

    def do_HEAD(self):
        if self.resp is None:
            self.send_response(404)
            self.send_header('Server', 'MicroServer')
            self.send_header('Connection', 'close')
            self.end_headers()
            return

        headers = self.resp.getHeaders()

        # set status codes
        status_code = self.resp.getStatus()
        self.send_response(status_code)

        # set headers
        for header in headers:
            if header == '':
                continue
            elif 'Content-Length' in header:
                self.send_header('Content-Length', '0')
                continue

            self.send_header(header, headers[header])

        self.end_headers()

    def do_POST(self):
        response_string = None
        chunkedResponse = False

        try:
            if self.resp is None:
                self.send_response(404)
                self.send_header('Server', 'MicroServer')
                self.send_header('Connection', 'close')
                self.end_headers()
                return
            else:
                verbose_print("Serving POST {0}...".format(
                    self.respLookupKey), end=' ')
                headers = self.resp.getHeaders()
                # set status codes
                status_code = self.resp.getStatus()
                self.send_response(status_code)
                # set headers
                for header in headers:
                    if header == '':
                        continue
                    elif 'Content-Length' in header:
                        length = headers[header]
                        self.send_header('Content-Length', str(length))
                        response_string = self.createDummyBodywithLength(
                            int(length))
                        continue
                    if 'Transfer-Encoding' in header:
                        self.send_header('Transfer-Encoding', 'Chunked')
                        response_string = '%X\r\n%s\r\n' % (
                            len('microserver'), 'microserver')
                        chunkedResponse = True
                        continue

                    self.send_header(header, headers[header])

                # TODO: temp fix, real fix should be in traffic dump or sanitizer
                if chunkedResponse:
                    pass
                elif response_string != None and response_string != '':
                    pass
                elif self.resp.getContentSize():
                    print("injecting content-length header..", end=' ')
                    self.send_header('Content-Length',
                                     str(self.resp.getContentSize()))

                self.end_headers()

            if chunkedResponse:
                print("Chunked responding")
                self.writeChunkedData()
            elif response_string != None and response_string != '':
                print("writing body as normal")
                self.wfile.write(bytes(response_string, 'UTF-8'))
            elif self.resp.getContentSize():
                print("artificially generating body based on content size")
                self.wfile.write(bytes(self.createDummyBodywithLength(
                    int(self.resp.getContentSize())), 'UTF-8'))

            verbose_print("Finished")
        except:
            e = sys.exc_info()
            print("Error in POST handling {0}".format(self.respLookupKey), e)
            self.send_response(400)
            self.send_header('Connection', 'close')
            self.end_headers()
