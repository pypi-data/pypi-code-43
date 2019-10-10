import socket
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler
from ssl         import wrap_socket as ssl_wrap_socket
from json        import loads as json_loads

from lib.pyHTTPInterface import Request, HTTPMethods
from lib.pyGenericPath.URL import URL


class HTTPRequestHandler(BaseHTTPRequestHandler):
	router = None

	def log_message(self, format, *args):
		super().log_message(format, *args)
		print(format)
		print(args)

	def handle_one_request(self):
		"""Handle a single HTTP request.

		 You normally don't need to override this method; see the class
		 __doc__ string for information on how to handle specific HTTP
		 commands such as GET and POST.

		 """
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
			self.do()
			# mname = 'do_' + self.command
			# if not hasattr(self, mname):
			# 	self.send_error(
			# 		HTTPStatus.NOT_IMPLEMENTED,
			# 		"Unsupported method (%r)" % self.command)
			# 	return
			# method = getattr(self, mname)
			# method()
			self.wfile.flush()  # actually send the response if not already done.
		except socket.timeout as e:
			# a read or a write timed out.  Discard this connection
			self.log_error("Request timed out: %r", e)
			self.close_connection = True
			return

	def do(self):
		headers = {}
		for key, value in self.headers.items():
			headers[key] = value

		httpMethod = HTTPMethods.from_simple_str(self.command)

		request = Request(
			httpMethod=httpMethod,
			path=URL.Parse(self.path),
			headers=headers,
			content="" # self.rfile.read()
		)

		self.router.Serve(request)

		print("=" * 20)
		print(request)
		print("=" * 20)

		self.send_response(200)
		self.end_headers()
		self.wfile.write(b'Hello, world!')

	def __call__(self, *args, **kwargs):
		return self

	# def do_POST(self):
	# 	print("=" * 20)
	# 	print(self.headers)
	# 	print("=" * 20)
	#
	# 	content_len = int(self.headers['Content-Length'])
	# 	post_body = self.rfile.read(content_len)
	# 	test_data = json_loads(post_body)
	#
	# 	print(test_data)
	#
	# 	self.send_response(200)
	# 	self.end_headers()
	# 	self.wfile.write(b'Hello, world!')


	# def do_PUT(self):
	# 	pass
	#
	# def do_PATCH(self):
	# 	pass
	#
	# def do_DELETE(self):
	# 	pass
	#
	# def do_HEAD(self):
	# 	pass
	#
	# def do_OPTIONS(self):
	# 	pass


class Server():
	def __init__(self, httpServerConfig, router):

		HTTPRequestHandler.router = router
		self.httpd = HTTPServer((httpServerConfig.hostname, httpServerConfig.port), HTTPRequestHandler)

		if (httpServerConfig.tls is not False):
			self.httpd.socket = ssl_wrap_socket(
				self.httpd.socket,
		    keyfile="path/to/key.pem",
		    certfile='path/to/cert.pem',
				server_side=True
			)

	def run(self):
		self.httpd.serve_forever()
