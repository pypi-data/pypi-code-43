from . import response_codes


class OpenADRInterfaceException(Exception):
    """
    Use this exception when an error should be sent to the VTN as an oadrResponse
    payload.

    :param message:    message to send back to the VTN (and potentially log)
    :param error_code: error code taken from ``pyoadr_ven.response_codes``
    """

    def __init__(self, message, error_code, *args):
        super().__init__(message, *args)
        self.error_code = error_code
        self.message = message


class BadDataError(OpenADRInterfaceException):
    def __init__(self, message, *args):
        super().__init__(message, response_codes.OADR_BAD_DATA, *args)


class OpenADRInternalException(Exception):
    """
    Use this exception when an error should be logged but not sent to the VTN.
    """

    def __init__(self, message, *args):
        super().__init__(message, *args)
        self.message = message


class InvalidStatusException(OpenADRInternalException):
    def __init__(self, message, *args):
        super().__init__(message, *args)
