#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
from cdumay_error import Error, NotImplemented, ValidationError, NotFound, \
    ErrorSchema


class MultipleChoices(Error):
    """Multiple choices"""
    MSGID = "HTTP-15978"
    CODE = 300


class MovedPermanently(Error):
    """Moved Permanently"""
    MSGID = "HTTP-30785"
    CODE = 301


class Found(Error):
    """Found"""
    MSGID = "HTTP-06627"
    CODE = 302


class SeeOther(Error):
    """See Other"""
    MSGID = "HTTP-05027"
    CODE = 303


class NotModified(Error):
    """Not Modified"""
    MSGID = "HTTP-22313"
    CODE = 304


class UseProxy(Error):
    """Use Proxy"""
    MSGID = "HTTP-08625"
    CODE = 305


class SwitchProxy(Error):
    """Switch Proxy"""
    MSGID = "HTTP-27946"
    CODE = 306


class TemporaryRedirect(Error):
    """Temporary Redirect """
    MSGID = "HTTP-03565"
    CODE = 307


class PermanentRedirect(Error):
    """Permanent Redirect"""
    MSGID = "HTTP-16866"
    CODE = 308


class Unauthorized(Error):
    """Unauthorized"""
    MSGID = "HTTP-28015"
    CODE = 401


class PaymentRequired(Error):
    """Payment Required"""
    MSGID = "HTTP-23516"
    CODE = 402


class Forbidden(Error):
    """Forbidden"""
    MSGID = "HTTP-29860"
    CODE = 403


class MethodNotAllowed(Error):
    """Method Not Allowed"""
    MSGID = "HTTP-00324"
    CODE = 405


class NotAcceptable(Error):
    """Not Acceptable"""
    MSGID = "HTTP-30133"
    CODE = 406


class ProxyAuthenticationRequired(Error):
    """Proxy Authentication Required"""
    MSGID = "HTTP-32405"
    CODE = 407


class RequestTimeout(Error):
    """Request Time-out"""
    MSGID = "HTTP-13821"
    CODE = 408


class Conflict(Error):
    """Conflict"""
    MSGID = "HTTP-21124"
    CODE = 409


class Gone(Error):
    """Gone"""
    MSGID = "HTTP-15611"
    CODE = 410


class LengthRequired(Error):
    """Length Required"""
    MSGID = "HTTP-08449"
    CODE = 411


class PreconditionFailed(Error):
    """Precondition Failed"""
    MSGID = "HTTP-02225"
    CODE = 412


class PayloadTooLarge(Error):
    """Payload Too Large"""
    MSGID = "HTTP-06608"
    CODE = 413


class URITooLong(Error):
    """URI Too Long"""
    MSGID = "HTTP-04901"
    CODE = 414


class UnsupportedMediaType(Error):
    """Unsupported media type"""
    MSGID = "HTTP-32471"
    CODE = 415


class RangeNotSatisfiable(Error):
    """Range Not Satisfiable"""
    MSGID = "HTTP-25512"
    CODE = 416


class ExpectationFailed(Error):
    """Expectation Failed"""
    MSGID = "HTTP-10663"
    CODE = 417


class Teapot(Error):
    """I'm a teapot"""
    MSGID = "HTTP-30106"
    CODE = 418


class MisdirectedRequest(Error):
    """Misdirected Request"""
    MSGID = "HTTP-24099"
    CODE = 421


class UnprocessableEntity(Error):
    """Unprocessable Entity"""
    MSGID = "HTTP-30485"
    CODE = 422


class Locked(Error):
    """Locked"""
    MSGID = "HTTP-28558"
    CODE = 423


class FailedDependency(Error):
    """Failed Dependency"""
    MSGID = "HTTP-26893"
    CODE = 424


class UpgradeRequired(Error):
    """Upgrade Required"""
    MSGID = "HTTP-03920"
    CODE = 426


class PreconditionRequired(Error):
    """Precondition Required"""
    MSGID = "HTTP-20303"
    CODE = 428


class TooManyRequests(Error):
    """Too Many Requests"""
    MSGID = "HTTP-10469"
    CODE = 429


class RequestHeaderFieldsTooLarge(Error):
    """Request Header Fields Too Large"""
    MSGID = "HTTP-26409"
    CODE = 431


class UnavailableForLegalReasons(Error):
    """Unavailable For Legal Reasons"""
    MSGID = "HTTP-19055"
    CODE = 451


class InternalServerError(Error):
    """Internal Server Error"""
    MSGID = "HTTP-02752"
    CODE = 500


class ProxyError(Error):
    """Proxy Error"""
    MSGID = "HTTP-09927"
    CODE = 502


class ServiceUnavailable(Error):
    """Service Unavailable"""
    MSGID = "HTTP-26820"
    CODE = 503


class GatewayTimeout(Error):
    """Gateway Time-out"""
    MSGID = "HTTP-04192"
    CODE = 504


class HTTPVersionNotSupported(Error):
    """HTTP Version Not Supported"""
    MSGID = "HTTP-00083"
    CODE = 505


class VariantAlsoNegotiates(Error):
    """Variant Also Negotiates"""
    MSGID = "HTTP-07221"
    CODE = 506


class InsufficientStorage(Error):
    """Insufficient Storage"""
    MSGID = "HTTP-02356"
    CODE = 507


class LoopDetected(Error):
    """Loop Detected"""
    MSGID = "HTTP-21955"
    CODE = 508


class NotExtended(Error):
    """Not Extended"""
    MSGID = "HTTP-30281"
    CODE = 510


class NetworkAuthenticationRequired(Error):
    """Network Authentication Required"""
    MSGID = "HTTP-30654"
    CODE = 511


HTTP_STATUS_CODES = {
    300: MultipleChoices,
    301: MovedPermanently,
    302: Found,
    303: SeeOther,
    304: NotModified,
    305: UseProxy,
    306: SwitchProxy,
    307: TemporaryRedirect,
    308: PermanentRedirect,
    400: ValidationError,
    401: Unauthorized,
    402: PaymentRequired,
    403: Forbidden,
    404: NotFound,
    405: MethodNotAllowed,
    406: NotAcceptable,
    407: ProxyAuthenticationRequired,
    408: RequestTimeout,
    409: Conflict,
    410: Gone,
    411: LengthRequired,
    412: PreconditionFailed,
    413: PayloadTooLarge,
    414: URITooLong,
    415: UnsupportedMediaType,
    416: RangeNotSatisfiable,
    417: ExpectationFailed,
    418: Teapot,
    421: MisdirectedRequest,
    422: UnprocessableEntity,
    423: Locked,
    424: FailedDependency,
    426: UpgradeRequired,
    428: PreconditionRequired,
    429: TooManyRequests,
    431: RequestHeaderFieldsTooLarge,
    451: UnavailableForLegalReasons,
    500: InternalServerError,
    501: NotImplemented,
    502: ProxyError,
    503: ServiceUnavailable,
    504: GatewayTimeout,
    505: HTTPVersionNotSupported,
    506: VariantAlsoNegotiates,
    507: InsufficientStorage,
    508: LoopDetected,
    510: NotExtended,
    511: NetworkAuthenticationRequired
}


def from_status(status, message=None, extra=None):
    """ Try to create an error from status code

    :param int status: HTTP status
    :param str message: Body content
    :param dict extra: Additional info
    :return: An error
    :rtype: cdumay_rest_client.errors.Error
    """
    if status in HTTP_STATUS_CODES:
        return HTTP_STATUS_CODES[status](message=message, extra=extra)
    else:
        return Error(
            code=status, message=message if message else "Unknown Error",
            extra=extra
        )


def from_response(response, url):
    """ Try to create an error from a HTTP response

    :param request.Response response: HTTP response
    :param str url: URL attained
    :return: An error
    :rtype: cdumay_rest_client.errors.Error
    """
    extra = dict(
        url=url, response=response.text, headers=dict(response.headers)
    )
    # noinspection PyBroadException
    try:
        data = response.json()
        data['extra'] = extra
        if not isinstance(data, dict):
            return from_status(response.status_code, response.text, extra=extra)

        code = data.get('code', response.status_code)
        if code in HTTP_STATUS_CODES:
            return HTTP_STATUS_CODES[code](**ErrorSchema().load(data))
        else:
            return Error(**ErrorSchema().load(data))
    except Exception:
        return from_status(response.status_code, response.text, extra=extra)
