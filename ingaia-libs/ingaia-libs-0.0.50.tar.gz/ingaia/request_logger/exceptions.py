from ingaia.commons.exceptions import GenericException


class RequestLoggerException(GenericException):
    message = 'An error occurred saving the request'

