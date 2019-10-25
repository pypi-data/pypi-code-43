# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""A module that contains definitions of custom exception classes."""

from automl.client.core.common.exceptions import ClientException, ConfigException, DataException
from automl.client.core.common._error_response_constants import ErrorCodes


# TODO Remove this
class AzureMLForecastException(Exception):
    """Base exception class for all exceptions in the Azure ML Forecasting toolkit."""

    pass


class PipelineException(ClientException):
    """
    Exception raised for errors in AzureMLForecastPipeline.

    Attributes:
        message: terse error message as defined in 'Messages' class of the
            'verify' module
        error_detail: optional, detailed error message

    """

    def __init__(self, exception_message, error_detail=None):
        """Create a PipelineException."""
        if error_detail is not None:
            super().__init__(exception_message="PipelineException: {0}, {1}".format(exception_message, error_detail))
        else:
            super().__init__(exception_message="PipelineException: {0}".format(exception_message))


class TransformException(ClientException):
    """
    Exception raised for errors in a transform class in the AzureML Forecasting SDK.

    Attributes:
        message: terse error message as defined in 'Messages' class of the 'verify' module
        error_detail: optional, detailed error message

    """

    def __init__(self, exception_message, error_detail=None):
        """Create a TransformException."""
        if error_detail is not None:
            super().__init__(exception_message="TransformException: {0}, {1}".format(exception_message, error_detail))
        else:
            super().__init__(exception_message="TransformException: {0}".format(exception_message))


class TransformValueException(TransformException):
    """
    Exception raised for value errors in a transform class in the AzureML Forecasting SDK.

    :param message:
        terse error message as defined in 'Messages'
        class of the 'verify' module
    :type message: str

    :param error_detail: optional, detailed error message
    :type error_detail: str
    """

    def __init__(self, exception_message, error_detail=None):
        """Create a TransformValueException."""
        if error_detail is not None:
            super().__init__("TransformValueException: {0}, {1}"
                             .format(exception_message, error_detail))
        else:
            super().__init__("TransformValueException: {0}".format(exception_message))


# TODO: Remove this exception.
class TransformTypeException(TransformException):
    """
    Exception raised for type errors in a transform class in the AzureML Forecasting SDK.

    :param message:
        terse error message as defined in 'Messages'
        class of the 'verify' module
    :type message: str

    :param error_detail: optional, detailed error message
    :type error_detail: str
    """

    def __init__(self, exception_message, error_detail=None):
        """Create a TransformTypeException."""
        if error_detail is not None:
            super().__init__("TransformTypeException: {0}, {1}"
                             .format(exception_message, error_detail))
        else:
            super().__init__("TransformTypeException: {0}".format(exception_message))


class NotTimeSeriesDataFrameException(ClientException):
    """
    Exception raised if the data frame is not of TimeSeriesDataFrame.

    Attributes:
        message: terse error message as defined in 'Messages' class of the 'verify' module
        error_detail: optional, detailed error message

    """

    def __init__(self, exception_message, error_detail=None):
        """Create a NotTimeSeriesDataFrameException."""
        if error_detail is not None:
            super().__init__(exception_message="NotTimeSeriesDataFrameException: {0}, {1}".format(
                exception_message, error_detail))
        else:
            super().__init__(exception_message="NotTimeSeriesDataFrameException: {0}".format(exception_message))


# TODO: remove this exception.
class NotSupportedException(ConfigException):
    """NotSupportedException."""

    def __init__(self, exception_message, error_detail=None):
        """Create a NotSupportedException."""
        if error_detail is not None:
            super().__init__("NotSupportedException: {0}, {1}".format(exception_message, error_detail))
        else:
            super().__init__("NotSupportedException: {0}".format(exception_message))


class DataFrameTypeException(DataException):
    """DataFrameTypeException."""

    def __init__(self, exception_message):
        """Create a DataFrameTypeException."""
        super().__init__("Data frame type is invalid. {0}".format(exception_message))


class DataFrameValueException(ClientException):
    """DataFrameValueException."""

    def __init__(self, exception_message, has_pii=False):
        """Create a DataFrameValueException."""
        super().__init__("Data frame value is invalid. {0}".format(exception_message))
        self._has_pii = has_pii


class ForecastingDataException(DataException):
    """The data exception, accepting both generic and privat information-containing exception."""

    def __init__(self, exception_message, pii_message=None, target=None):
        """Create a DataFrameFrequencyException."""
        if pii_message is not None:
            super().__init__(pii_message, target)
            self._has_pii = True
            self._generic_msg = exception_message
        else:
            super().__init__(exception_message, target)


class DataFrameFrequencyException(ForecastingDataException):
    """DataFrameFrequencyException."""

    _error_code = ErrorCodes.TIMEFREQUENCYCANNOTBEINFERRABLE_ERROR


class DataFrameFrequencyChanged(ForecastingDataException):
    """Frequency is different in train and test/validate set."""

    _error_code = ErrorCodes.FREQUENCIESMISMATCH_ERROR


class DataFrameTimeNotContinuous(ForecastingDataException):
    """There is a gap between train and test."""

    _error_code = ErrorCodes.TIMENOTCONTINUOUS_ERROR


class DataFrameMissingColumnException(ForecastingDataException):
    """DataFrameMissingColumnException."""

    _error_code = ErrorCodes.MISSINGCOLUMN_ERROR

    TIME_COLUMN = "Time"
    GRAIN_COLUMN = "Grain"
    GROUP_COLUMN = "Group"
    ORIGIN_COLUMN = "Origin"
    VALUE_COLUMN = "TargetValue"
    REGULAR_COLUMN = "Regular"

    def __init__(self, pii_message=None, target=REGULAR_COLUMN):
        """Create a DataFrameMissingTimeColumnException."""
        super().__init__("Data frame is missing a column.", pii_message, target)


# TODO: remove this exception.
class DatetimeConversionException(DataException):
    """DatetimeConversionException."""

    def __init__(self, message):
        """Create a DateTimeConversionException."""
        super().__init__("Unable to do datetime conversion. {0}".format(message))


class DataFrameIncorrectFormatException(ForecastingDataException):
    """DataFrameIncorrectFormatException."""

    pass


class DuplicatedIndexException(ForecastingDataException):
    """DuplicatedIndexException."""

    _error_code = ErrorCodes.DUPLICATEDINDEX_ERROR


class ForecastingConfigException(ConfigException):
    """The config exceptions related to forecasting tasks."""

    _error_code = ErrorCodes.FORECASTINGCONFIG_ERROR


class ColumnTypeNotSupportedException(ForecastingConfigException):
    """ColumnTypeNotSupportedException."""

    _error_code = ErrorCodes.COLUMNNAMENOTSUPPORTED_ERROR

    def __init__(self, exception_message, error_detail=None):
        """Create a ColumnTypeNotSupportedException."""
        if error_detail is not None:
            super().__init__("ColumnTypeNotSupportedException: {0}, {1}".format(exception_message, error_detail))
        else:
            super().__init__("ColumnTypeNotSupportedException: {0}".format(exception_message))


class DropSpecialColumn(ForecastingConfigException):
    """DropSpecialColumn."""

    _error_code = ErrorCodes.SPECIALCOLUMNDROP_ERROR


class GrainAndTimeOverlapException(ForecastingConfigException):
    """GrainAndTimeOverlapException."""

    _error_code = ErrorCodes.TIMEANDGRAINSOVERLAP_ERROR


class InvalidTsdfArgument(ConfigException):
    """Invalid tsdf argument."""

    _error_code = ErrorCodes.BADARGUMENT_ERROR


class WrongShapeDataError(ForecastingDataException):
    """The class of errors related to the data frame shape."""

    _error_code = ErrorCodes.DATASHAPE_ERROR


class GrainAbsent(ForecastingDataException):
    """The class of errors when grain is present in test/validate, but not in train set."""

    _error_code = ErrorCodes.GRAINISABSENT_ERROR
