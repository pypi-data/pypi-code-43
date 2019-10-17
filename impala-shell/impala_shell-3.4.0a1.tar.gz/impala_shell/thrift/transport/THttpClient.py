#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#

from io import BytesIO
import httplib
import os
import socket
import sys
import urllib
import urlparse
import warnings

from TTransport import *


class THttpClient(TTransportBase):
  """Http implementation of TTransport base."""

  def __init__(self, uri_or_host, port=None, path=None, cafile=None, cert_file=None, key_file=None, ssl_context=None):
    """THttpClient supports two different types of constructors.

    THttpClient(host, port, path) - deprecated
    THttpClient(uri, [port=<n>, path=<s>, cafile=<filename>, cert_file=<filename>, key_file=<filename>, ssl_context=<context>])

    Only the second supports https.  To properly authenticate against the server,
    provide the client's identity by specifying cert_file and key_file.  To properly authenticate the server,
    specify either cafile or ssl_context with a CA defined.
    NOTE: if both cafile and ssl_context are defined, ssl_context will override cafile.
    """
    if port is not None:
      warnings.warn(
        "Please use the THttpClient('http{s}://host:port/path') constructor",
        DeprecationWarning,
        stacklevel=2)
      self.host = uri_or_host
      self.port = port
      assert path
      self.path = path
      self.scheme = 'http'
    else:
      parsed = urlparse.urlparse(uri_or_host)
      self.scheme = parsed.scheme
      assert self.scheme in ('http', 'https')
      if self.scheme == 'http':
        self.port = parsed.port or httplib.HTTP_PORT
      elif self.scheme == 'https':
        self.port = parsed.port or httplib.HTTPS_PORT
        self.certfile = cert_file
        self.keyfile = key_file
        self.context = ssl.create_default_context(cafile=cafile) if (cafile and not ssl_context) else ssl_context
      self.host = parsed.hostname
      self.path = parsed.path
      if parsed.query:
        self.path += '?%s' % parsed.query
    self.__wbuf = BytesIO()
    self.__http = None
    self.__http_response = None
    self.__timeout = None
    self.__custom_headers = None

  def open(self):
    if self.scheme == 'http':
      self.__http = httplib.HTTPConnection(self.host, self.port, timeout=self.__timeout)
    else:
      self.__http = httplib.HTTPSConnection(self.host, self.port, key_file=self.keyfile,
            cert_file=self.certfile, timeout=self.__timeout, context=self.context)

  def close(self):
    self.__http.close()
    self.__http = None
    self.__http_response = None

  def isOpen(self):
    return self.__http is not None

  def setTimeout(self, ms):
    if not hasattr(socket, 'getdefaulttimeout'):
      raise NotImplementedError

    if ms is None:
      self.__timeout = None
    else:
      self.__timeout = ms / 1000.0

  def setCustomHeaders(self, headers):
    self.__custom_headers = headers

  def read(self, sz):
    return self.__http_response.read(sz)

  def write(self, buf):
    self.__wbuf.write(buf)

  def __withTimeout(f):
    def _f(*args, **kwargs):
      orig_timeout = socket.getdefaulttimeout()
      socket.setdefaulttimeout(args[0].__timeout)
      try:
        result = f(*args, **kwargs)
      finally:
        socket.setdefaulttimeout(orig_timeout)
      return result
    return _f

  def flush(self):
    if self.isOpen():
      self.close()
    self.open()

    # Pull data out of buffer
    data = self.__wbuf.getvalue()
    self.__wbuf = BytesIO()

    # HTTP request
    self.__http.putrequest('POST', self.path)

    # Write headers
    self.__http.putheader('Host', self.host)
    self.__http.putheader('Content-Type', 'application/x-thrift')
    self.__http.putheader('Content-Length', str(len(data)))

    if not self.__custom_headers or 'User-Agent' not in self.__custom_headers:
      user_agent = 'Python/THttpClient'
      script = os.path.basename(sys.argv[0])
      if script:
        user_agent = '%s (%s)' % (user_agent, urllib.quote(script))
      self.__http.putheader('User-Agent', user_agent)

    if self.__custom_headers:
        for key, val in self.__custom_headers.iteritems():
            self.__http.putheader(key, val)

    self.__http.endheaders()

    # Write payload
    self.__http.send(data)

    # Get reply to flush the request
    self.__http_response = self.__http.getresponse()
    self.code = self.__http_response.status
    self.message = self.__http_response.reason
    self.headers = self.__http_response.msg

  # Decorate if we know how to timeout
  if hasattr(socket, 'getdefaulttimeout'):
    flush = __withTimeout(flush)
