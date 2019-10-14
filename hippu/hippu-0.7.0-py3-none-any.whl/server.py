"""
Development notes:
    Naming attributes
        method -> verb (do something)
        property -> noun (value of)

    Handle -> _dispatch

More info about cookies:
    * https://docs.python.org/3/library/http.cookies.html
    * https://thoughtbot.com/blog/lucky-cookies
    * https://stackoverflow.com/questions/16305814/are-multiple-cookie-headers-allowed-in-an-http-request

"""
import inspect
import os
import logging
import socket
import sys
import time
import threading
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler
from http.server import HTTPServer

import collections

MountPoint = collections.namedtuple('MountPoint', 'path service')


# ThreadedHTTPServer is new in version 3.7. Following adds
# support for Python 3.5.
try:
    from http.server import ThreadedHTTPServer
except ImportError:
    from socketserver import ThreadingMixIn

    class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
        """ Handle requests in a separate thread. """

try:
    from PIL import Image, ImageDraw
except ImportError:
    pil_support = False
else:
    pil_support = True

from hippu import HTTP
from hippu.request import Request
from hippu.response import Response
from hippu.response import Status


log = logging.getLogger(__name__)


# Instead of BaseHTTPRequestHandler it could be possible to use
# SimpleHTTPRequestHandler.
class HTTPRequestHanlder(BaseHTTPRequestHandler):
    """
    Created per request.

    Handles requests.
    """
    # HTTP/1.1 is necessary for connection persistence (keepalive)
    #protocol_version = 'HTTP/1.1'
    timeout = 1

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    def send_response_headers(self, response):
        headers = response.headers

        # Set content-type header.
        if HTTP.CONTENT_TYPE not in headers:
            headers[HTTP.CONTENT_TYPE] = response.content_type

        if hasattr(response, '_cookie'):
            cookies_str = response.cookie.output(header='', sep=',')

            # Send cookies as separated headers. At least Chrome requires this
            # approach when operating in localhost.
            for c in cookies_str.split(','):
                self.send_header(HTTP.SET_COOKIE, c)

        if response._keep_alive:
            timeout, max_count = response._keep_alive
            headers[HTTP.CONNECTION] = HTTP.KEEP_ALIVE
            headers[HTTP.KEEP_ALIVE] = "timeout={}, max={}".format(timeout, max_count)

        headers[HTTP.CONTENT_LENGTH] = len(response)

        self.send_headers(headers)

    def send_headers(self, headers):
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()

    #
    # Overriding BaseHTTPRequestHandler's 'do_' methods.
    #

    def do_HEAD(self):
        self._handle()

    def do_GET(self):
        self._handle()

    def do_PUT(self):
        self._handle()

    def do_POST(self):
        self._handle()

    def do_PATCH(self):
        self._handle()

    def do_DELETE(self):
        self._handle()

    def do_TRACE(self):
        self._handle()

    def do_OPTIONS(self):
        self._handle()

    def do_CONNECT(self):
        self._handle()

    def _handle(self):
        t1 = time.time()

        req = Request(self)
        res = Response.create(self)

        # Log request.
        self.server.log_request(req)

        try:
            # Find first handler matching the request.
            handler = self._find_handler(req)
            # Resolve request.
            self._resolve(req, res, handler)
        except Exception as err:
            self.server.handle_internal_error(req, res, str(err))

        duration = round((time.time() - t1) * 1000, 3)

        log.debug("Serving request %s %s took %s ms.", req.method, req.path, duration)
        log.debug("")

    def _find_handler(self, req):
        """ Returns a handler matching the request. """

        for mount_path, service in self.server.services:
            if req.path.startswith(mount_path):
                # Relative path is the portion of the path following
                # the mount path.
                #
                # For example,
                #   >>> server.mount(service, '/mount/path')
                #
                #   HTTP GET http://localhost:8080/mount/path/resouce/path
                #
                #       full path: /mount/path/resouce/path
                #       mount path: /mount/path
                #       relative path: /resouce/path

                # relative_path = req.path.replace(mount_path, '/', 1)
                # handler = service.match(req, relative_path)

                req.path.base = mount_path
                handler = service.match(req)#, req.path.relative)

                if handler:
                    return handler

        # Favicon is considered as a special case (mainly because of
        # convenience). Favicon handler is called only if no other
        # handler was not found.
        if req.path == '/favicon.ico':
            return self.server.handle_favicon

        # No handler found. Calling server's not found handler.
        return self.server.handle_not_found

    def _resolve(self, req, res, handler):
        """ Resolve request by calling the handler. """
        handler(req, res)

        # Check data type, resolve content-type and do type conversion.
        res.finalize()

        # Send headers unless already sent.
        if not res.headers_sent:
            self.send_response(res.status_code)
            self.send_response_headers(res)

        # Sent message content as bytes
        if res.content:
            self.wfile.write(res.content)

    def log_message(self, format, *args):
        """ Log message is called by native http handler. """
        pass

    def handle(self):
        try:
            super().handle()
        except ConnectionResetError as err:
            log.warning(str(err))


class Server(ThreadedHTTPServer):
    """ Micro server. """
    _instances = None

    def __init__(self, address, protocol_version=1.1):
        self._serve_forever_evt = threading.Event()
        request_handler = HTTPRequestHanlder
        request_handler.protocol_version = 'HTTP/{}'.format(protocol_version)
        super().__init__(address, request_handler)
        # _services holds a list of mounted Route objects. Route matching
        # is started from the beginning of the list. First matching occurance
        # is returned.
        self._services = []

        self._stopped = threading.Event()

        # Verbose.
        log.debug("Server is listening on port %s at %s.", address[1], address[0])

    @classmethod
    def create(cls, address):
        """ Create server instance unless already exists.

        Server instance is created for unique host / port pairs. For example,
        calling code below will produce two instances:

            >>> Server.create(('127.0.0.1', 8080))
            >>> Server.create(('127.0.0.1', 8081))

        The same service can be mounted under both servers.
        """
        host, port = address

        if cls._instances is None:
            cls._instances = dict()

        if host not in cls._instances:
            cls._instances[host] = dict()

        if port not in cls._instances[host]:
            cls._instances[host][port] = cls(address)

        return cls._instances[host][port]

    @property
    def services(self):
        return self._services
        # for mp in self._services:
        #     yield mp.path, m

    def mount(self, service, path='/'):
        """ Mount a service under given path. """
        if not path.startswith('/'):
            path = '/' + path

        if not path.endswith('/'):
            path += '/'

        self._services.append(MountPoint(path, service))

    def unmount(self, service):
        """ Unmount service. """
        for mp in self._services:
            if mp.service == service:
                self._services.remove(mp)
                break

    def handle_favicon(self, reg, res):
        """ Handle favicon request.

        Usage:
            >>> httpd = Server()
            >>> httpd.handle_favicon = my_favicon_handler

        More info about favicon:
            https://www.w3.org/2005/10/howto-favicon
        """
        log.debug("Favicon request handled by default handler.")

        if pil_support:
            image = Image.new('RGBA', (32, 32), (255, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.ellipse((0, 0, 31, 31), fill='#6D8AB8')

            res.content_type = HTTP.IMAGE_PNG
            res.content = image
        else:
            res.status_code = 302

    #
    # Note: super().handle_error(request, client_address)
    #
    def handle_internal_error(self, req, res, msg):
        """ Handle erver error.

        Usage:
            >>> httpd = Server()
            >>> httpd.handle_internal_error = my_error_handler
        """
        log.error("Error occurred while serving %s %s", req.method, req.path, exc_info=True)

        res.headers.clear()
        res.status_code = Status.INTERNAL_SERVER_ERROR
        res.content = str(msg)

    def handle_not_found(self, req, res):
        """ Handle not found error.

        Usage:
            >>> httpd = Server()
            >>> httpd.handle_not_found = my_not_found_handler
        """
        log.warning("Not found {} {}".format(req.method, req.path))
        res.status_code = Status.NOT_FOUND

    def log_request(self, req):
        """ Note: Super already have log_request() method! """
        host, port = req.client_address
        # "127.0.0.1:8000 GET /path"
        log.debug("Request %s %s received from %s:%i.", req.method, req.path, host, port, )

    def serve_forever(self, *args, **kwargs):
        log.debug("Starting server.")
        self._serve_forever_evt.set()
        super().serve_forever(*args, **kwargs)

    def server_close(self):
        self._stopped.set()

        if self._serve_forever_evt.is_set():
            log.debug("Shutting down server.")
            super().shutdown()
            log.debug("Server is shut down.")

        log.debug("Closing server.")
        super().server_close()
        log.debug("Server is closed.")

    def is_stopped(self):
        return self._stopped.is_set()

    # def handle_error(self, request, client_address):
    #    pass

