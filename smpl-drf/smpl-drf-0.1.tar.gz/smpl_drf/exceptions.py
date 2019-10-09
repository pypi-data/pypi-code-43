
from rest_framework import status
from rest_framework import exceptions


class AuthenticationFailed(exceptions.APIException):
    status_code = status.HTTP_403_FORBIDDEN
