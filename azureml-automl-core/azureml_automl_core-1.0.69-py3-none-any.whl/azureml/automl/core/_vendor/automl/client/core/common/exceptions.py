# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Exceptions thrown by AutoML."""
import json
from typing import cast, Optional, Type, TypeVar, Any
from ._error_response_constants import ErrorCodes


ExceptionT = TypeVar('ExceptionT', bound='AutoMLException')


class ErrorTypes:
    """Possible types of errors."""

    User = 'User'
    Service = 'Service'
    Client = 'Client'
    Resource = 'Resource'
    Unclassified = 'Unclassified'
    All = {User, Service, Client, Resource, Unclassified}


class AutoMLException(Exception):
    """Exception with an additional field specifying what type of error it is."""

    error_type = ErrorTypes.Unclassified

    def __init__(self, exception_message="", error_type=ErrorTypes.Unclassified, target=None, details=None):
        """
        Construct a new AutoMLException.

        :param error_type: type of the exception.
        :param message: details on the exception.
        """
        super().__init__(exception_message)
        self.error_type = error_type
        self._exception_message = exception_message
        self._target = target
        self._details = details
        self._inner_exception = None     # type: Optional[BaseException]
        self._has_pii = False
        self._generic_msg = None            # type: Optional[str]

    def __repr__(self) -> str:
        """Return string representation of the exception."""
        return "{}:\n\tMessage: {}\n\tInnerException {}\n\tErrorResponse \n{}".format(
            self.__class__.__name__,
            self._exception_message,
            self._inner_exception,
            self._serialize_json(indent=4))

    def __str__(self) -> str:
        """Return string representation of the exception."""
        return self.__repr__()

    @classmethod
    def from_exception(cls: 'Type[ExceptionT]', e: BaseException, msg: Optional[str] = None,
                       target: Optional[str] = None, has_pii: bool = False) -> ExceptionT:
        """
        Convert an arbitrary exception to this exception type. The resulting exception is marked as containing PII.

        :param e: the original exception object
        :param msg: optional message to use instead of the original exception message
        :param target: optional string pointing to the target of the exception
        :param has_pii: whether this exception contains PII or not
        :return: a new exception of this type, preserving the original stack trace
        """
        if not msg and isinstance(e, cls):
            return cast(ExceptionT, e)
        new_exception = cast(ExceptionT, cls(exception_message=(msg or str(e)), target=target)
                             .with_traceback(e.__traceback__))
        new_exception._inner_exception = e
        new_exception._has_pii = has_pii
        return new_exception

    @classmethod
    def create_without_pii(cls: 'Type[ExceptionT]', msg: Optional[str] = None,
                           target: Optional[str] = None) -> ExceptionT:
        """
        Create an exception that is tagged as not containing PII.

        :param msg: optional message to use instead of the original exception message
        :param target: optional string pointing to the target of the exception
        :return:
        """
        exception = cls(exception_message=msg, target=target)
        exception._has_pii = False
        return exception

    def with_generic_msg(self: ExceptionT, msg: str) -> ExceptionT:
        """
        Attach a generic error message that will be used in telemetry if this exception contains PII.

        :param msg: the generic message to use
        :return: this object
        """
        self._generic_msg = msg
        self._has_pii = True
        return self

    @property
    def has_pii(self) -> bool:
        """Check whether this exception's message contains PII or not."""
        return cast(bool, getattr(self, '_has_pii', False))

    @property
    def pii_free_msg(self) -> str:
        """Fallback message to use for situations where printing PII-containing information is inappropriate."""
        return cast(str, getattr(self, '_generic_msg', None) or '[Hidden as it may contain PII]')

    def get_error_type(self):
        """Get the error code for this exception."""
        return getattr(self, "_error_code", self.error_type)

    def _serialize_json(self, indent: Optional[int] = None) -> str:
        """
        Serialize this exception as an ErrorResponse json.

        :return: json string
        """
        error_ret = {}
        error_out = {}  # type: Any
        for super_class in self.__class__.mro():
            if super_class.__name__ == AutoMLException.__name__:
                break
            try:
                error_code = getattr(super_class, '_error_code')
                if error_out != {}:
                    # Flatten the tree in case we have something like System > System > System > System
                    prev_code = error_out.get('code')
                    if prev_code is None or error_code != prev_code:
                        error_out = {"code": error_code, "inner_error": error_out}
                else:
                    error_out = {"code": error_code}
            except AttributeError:
                break

        error_out['message'] = self._exception_message
        if self._target is not None:
            error_out['target'] = self._target
        if self._details is not None:
            error_out['details'] = self._details
        error_ret['error'] = error_out

        return json.dumps(error_ret, indent=indent, sort_keys=True)


class UserException(AutoMLException):
    """
    Exception related to user error.

    :param exception_message: Details on the exception.
    """

    _error_code = ErrorCodes.USER_ERROR

    def __init__(self, exception_message="", target=None):
        """
        Construct a new UserException.

        :param exception_message: details on the exception.
        """
        super().__init__(exception_message, ErrorTypes.User, target)


class DataException(UserException):
    """
    Exception related to data validations.

    :param exception_message: Details on the exception.
    """

    _error_code = ErrorCodes.INVALIDDATA_ERROR

    def __init__(self, exception_message="", target=None):
        """
        Construct a new DataException.

        :param exception_message: details on the exception.
        """
        super().__init__(exception_message, target)


class UntrainedModelException(UserException):
    """UntrainedModelException."""

    def __init__(self, exception_message="Fit need to be called before predict."):
        """Create a UntrainedModelException."""
        super().__init__("UntrainedModelException: {0}".format(exception_message))


class ConfigException(AutoMLException):
    """
    Exception related to invalid user config.

    :param exception_message: Details on the exception.
    """

    _error_code = ErrorCodes.VALIDATION_ERROR

    def __init__(self, exception_message="", target=None):
        """
        Construct a new ConfigException.

        :param exception_message: details on the exception.
        """
        super().__init__(exception_message, ErrorTypes.User, target)


class ArgumentException(AutoMLException):
    """
    Exception related to invalid user config.

    :param exception_message: Details on the exception.
    """

    _error_code = ErrorCodes.VALIDATION_ERROR

    def __init__(self, exception_message="", target=None):
        """
        Construct a new ConfigException.

        :param exception_message: details on the exception.
        """
        super().__init__(exception_message, ErrorTypes.User, target)


class ServiceException(AutoMLException):
    """
    Exception related to JOS.

    :param exception_message: Details on the exception.
    """

    _error_code = ErrorCodes.SYSTEM_ERROR

    def __init__(self, exception_message="", target=None):
        """
        Construct a new ServiceException.

        :param exception_message: details on the exception.
        """
        super().__init__(exception_message, ErrorTypes.Service, target)


class ClientException(AutoMLException):
    """
    Exception related to client.

    :param exception_message: Details on the exception.
    """

    _error_code = ErrorCodes.SYSTEM_ERROR

    def __init__(self, exception_message="", target=None):
        """
        Construct a new ClientException.

        :param exception_message: details on the exception.
        """
        super().__init__(exception_message, ErrorTypes.Client, target)


class FitException(ClientException):
    """
    Exception related to fit in external pipelines, models, and transformers.

    :param message: Details on the exception.
    """

    _error_code = ErrorCodes.FIT_ERROR

    def __init__(self, exception_message="", target=None):
        """
        Construct a new FitException.

        :param exception_message: details on the exception.
        """
        super().__init__(exception_message, target)


class TransformException(ClientException):
    """
    Exception related to transform in external pipelines and transformers.

    :param exception_message: Details on the exception.
    """

    _error_code = ErrorCodes.TRANSFORM_ERROR

    def __init__(self, exception_message="", target=None):
        """
        Construct a new TransformException.

        :param message: details on the exception.
        """
        super().__init__(exception_message, target)


class DataErrorException(AutoMLException):
    """
    Exception related to errors seen while processing data at training or inference time.

    :param exception_message: Details on the exception.
    """

    _error_code = ErrorCodes.DATA_ERROR

    def __init__(self, exception_message="", target=None):
        """
        Construct a new DataErrorException.

        :param exception_message: details on the exception.
        """
        super().__init__(exception_message, ErrorTypes.Client, target)


class RawDataSnapshotException(AutoMLException):
    """
    Exception related to capturing the raw data snapshot to be used at the inference time.

    :param exception_message: Details on the exception.
    """

    _error_code = ErrorCodes.RAWDATASNAPSHOT_ERROR

    def __init__(self, exception_message="", target=None):
        """
        Construct a new RawDataSnapshotException.

        :param exception_message: details on the exception.
        """
        super().__init__(exception_message, ErrorTypes.Client, target)


class ResourceException(AutoMLException):
    """
    Exception related to resource usage.

    :param exception_message: Details on the exception.
    """

    def __init__(self, exception_message="", target=None):
        """
        Construct a new ResourceException.

        :param exception_message: details on the exception.
        """
        super().__init__(exception_message, ErrorTypes.Resource, target)


class OnnxConvertException(ClientException):
    """Exception related to ONNX convert."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.ONNX_ERROR


class DataprepException(ClientException):
    """Exceptions related to Dataprep."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.DATAPREPVALIDATION_ERROR
