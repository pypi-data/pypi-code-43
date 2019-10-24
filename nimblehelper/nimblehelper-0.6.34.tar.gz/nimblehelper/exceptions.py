from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from .settings import INVALID_INPUT, INVALID_AUTHORIZATION, INTERNAL_SERVER_ERROR


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status'] = response.status_code
    return response


class BadInputException(APIException):
    status_code = 400
    default_detail = INVALID_INPUT


class InvalidAuthentication(APIException):
    status_code = 401
    default_detail = INVALID_AUTHORIZATION


class InternalServerError(APIException):
    status_code = 500
    default_detail = INTERNAL_SERVER_ERROR
