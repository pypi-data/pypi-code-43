from enum import IntEnum
import io
import json
import logging
from http.cookies import SimpleCookie

try:
    from PIL import Image
except ImportError:
    pil_support = False
else:
    pil_support = True

from hippu import HTTP

log = logging.getLogger(__name__)


class Status(IntEnum):
    """ HTTP response status codes.

    More info:
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

    """

    #
    # 1xx INFORMATIONAL
    #
    CONTINUE = 100
    SWITCHING_PROTOCOLS = 101
    PROCESSING = 102
    #
    # 2×× SUCCESS
    #
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NON_AUTHORITATIVE_INFORMATION = 203
    NO_CONTENT = 204
    RESET_CONTENT = 205
    PARTIAL_CONTENT = 206
    MULTI_STATUS = 207
    ALREADY_REPORTED = 208
    IM_USED = 226
    #
    # 3×× REDIRECTION
    #
    MULTIPLE_CHOICES = 300
    MOVED_PERMANENTLY = 301
    FOUND = 302
    SEE_OTHER = 303
    NOT_MODIFIED = 304
    USE_PROXY = 305
    TEMPORARY_REDIRECT = 307
    PERMANENT_REDIRECT = 308
    #
    # 4×× CLIENT_ERROR
    #
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    NOT_ACCEPTABLE = 406
    PROXY_AUTHENTICATION_REQUIRED = 407
    REQUEST_TIMEOUT = 408
    CONFLICT = 409
    GONE = 410
    LENGTH_REQUIRED = 411
    PRECONDITION_FAILED = 412
    PAYLOAD_TOO_LARGE = 413
    REQUEST_URI_TOO_LONG = 414
    UNSUPPORTED_MEDIA_TYPE = 415
    REQUESTED_RANGE_NOT_SATISFIABLE = 416
    EXPECTATION_FAILED = 417
    IM_A_TEAPOT = 418
    MISDIRECTED_REQUEST = 421
    UNPROCESSABLE_ENTITY = 422
    LOCKED = 423
    FAILED_DEPENDENCY = 424
    UPGRADE_REQUIRED = 426
    PRECONDITION_REQUIRED = 428
    TOO_MANY_REQUESTS = 429
    REQUEST_HEADER_FIELDS_TOO_LARGE = 431
    CONNECTION_CLOSED_WITHOUT_RESPONSE = 444
    UNAVAILABLE_FOR_LEGAL_REASONS = 451
    CLIENT_CLOSED_REQUEST = 499
    #
    # 5×× SERVER_ERROR
    #
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    HTTP_VERSION_NOT_SUPPORTED = 505
    VARIANT_ALSO_NEGOTIATES = 506
    INSUFFICIENT_STORAGE = 507
    LOOP_DETECTED = 508
    NOT_EXTENDED = 510
    NETWORK_AUTHENTICATION_REQUIRED = 511
    NETWORK_CONNECT_TIMEOUT_ERROR = 599


class Response:
    def __init__(self, exchange):
        self._exchange = exchange
        # Note: Requests lib uses matching 'status_code' attribute.
        self.status_code = Status.OK
        # Content type is determined and set by the server unless
        # explicitly set.
        self.content_type = None
        self._data = None
        self.headers = {}
        self.headers_sent = False
        self._keep_alive = None
        self.encoding = 'UTF-8'

    def __len__(self):
        if self._data:
            return len(self._data)
        return 0

    @classmethod
    def create(self, exchange):
        return Response(exchange)

    @property
    def content(self):
        return self._data

    @content.setter
    def content(self, data):
        # Content type is determined and set by the server if not set explicitely.
        self._data = data

    @property
    def text(self):
        return self.content.decode('utf-8')

    def set_header(self, key, value):
        #
        # Converting headers to all lower case to simplify following
        # operations.
        #
        # HTTP header names are case-insensitive, according to RFC 2616:
        #   Each header field consists of a name followed by a colon (":")
        #   and the field value. Field names are case-insensitive.
        #
        #   [https://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html#sec4.2]
        #
        self.headers[key.lower()] = value

    def get_header(self, key, default=None):
        return self.headers.get(key.lower(), default)

    def send_status(self, code):
        """ Send response status code. """
        self._exchange.send_response(code)

    def send_header(self, key, value):
        """ Send single HTTP header. """
        self._exchange.send_header(key, value)
        self.headers_sent = True

    def send_headers(self, headers):
        """ Send response headers. """
        self._exchange.send_headers(headers)
        self.headers_sent = True

    def keep_alive(self, timeout=10, max_count=100):
        self._keep_alive = (timeout, max_count)

    def write(self, data):
        """ Write data. """
        self._exchange.wfile.write(data)

    @property
    def cookie(self):
        if not hasattr(self, '_cookie'):
            self._cookie = SimpleCookie()
        return self._cookie

    def finalize(self):
        """ Converts data into bytes and resolves content-type and
        encoding.

        Server will call finalize() method just before send. Filters
        will be applied before this.
        """
        data = self._data
        content_type = self.content_type

        # Use content-type and encoding set.
        if isinstance(data, bytes):
            pass

        # Strings are encoded by using response encoding type.
        elif isinstance(data, str):
            self.content = data.encode(self.encoding)
            self.content_type = HTTP.TEXT_HTML

        # Strings are encoded by using response encoding type.
        elif isinstance(data, (int, float)):
            self.content = str(data).encode(self.encoding)
            self.content_type = HTTP.TEXT_HTML

        # Dicts, lists and tuples will be converted to bytes by using
        # standard json library.
        elif isinstance(data, (dict, list, tuple)):
            data = json.dumps(data, default=to_json)
            self.content = data.encode(self.encoding)
            self.content_type = HTTP.APPLICATION_JSON

        # PIL images are returned in png format.
        elif pil_support and isinstance(data, Image.Image):
            if not content_type:
                img_frmt = 'png'
                content_type = HTTP.IMAGE_PNG
            elif content_type == HTTP.IMAGE_BMP:
                img_frmt = 'bmp'
            elif content_type == HTTP.IMAGE_GIF:
                img_frmt = 'gif'
            elif content_type == HTTP.IMAGE_JPEG:
                img_frmt = 'jpeg'
            elif content_type == HTTP.IMAGE_PNG:
                img_frmt = 'png'
            elif content_type == HTTP.IMAGE_ICO:
                img_frmt = 'ico'
            else:
                log.warning("Content-type '{}' does not match the content (PIL Image).")
                img_frmt = 'png'
                content_type = HTTP.IMAGE_PNG

            with io.BytesIO() as f:
                data.save(f, format=img_frmt)
                self.content = f.getvalue()

            self.content_type = HTTP.IMAGE_PNG

        # Content type is set as text/html but the content is not string.
        elif content_type == HTTP.TEXT_HTML and not isinstance(data, str):
            self.content = str(self.content).encode(self.encoding)

        elif hasattr(data, '__iter__'):
            data = json.dumps(dict(data), default=to_json)
            self.content = data.encode(self.encoding)
            self.content_type = HTTP.APPLICATION_JSON


def to_json(o):
    """
    Example:
        def to_dict(self):
            return dict(name=self.name, id=self.id)

        def __iter__(self):
            return iter([('name', self.name), ('id', self.id)])
    """
    if hasattr(o, 'to_dict'):
        return o.to_dict()
    return dict(o)
