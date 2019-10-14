# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The set of custom exceptions produced by AutoMl package."""

from azureml._common.exceptions import AzureMLException
from azureml._common._error_response._error_response_constants import ErrorCodes
from azureml.exceptions import UserErrorException
from automl.client.core.common import exceptions


class ConfigException(UserErrorException, exceptions.ConfigException):
    """Exception related to invalid user config."""

    _error_code = ErrorCodes.VALIDATION_ERROR


# TODO this should move to azureml.exceptions
class ValidationException(UserErrorException, exceptions.DataException):
    """Exception for any errors caught when validating inputs."""

    _error_code = ErrorCodes.VALIDATION_ERROR


# TODO this should move to azureml.exceptions
class DataException(ValidationException, exceptions.DataException):
    """Exception related to data validations."""

    _error_code = ErrorCodes.INVALIDDATA_ERROR


# TODO this should move to azureml.exceptions
class SystemException(AzureMLException):
    """Exception for internal errors that happen within the SDK."""

    _error_code = ErrorCodes.SYSTEM_ERROR


class ServiceException(SystemException):
    """Exception related to JOS."""

    _error_code = ErrorCodes.SERVICE_ERROR


class ClientException(AzureMLException, exceptions.ClientException):
    """Exception related to client."""

    _error_code = ErrorCodes.SYSTEM_ERROR


class OnnxConvertException(ClientException):
    """Exception related to ONNX convert."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.ONNX_ERROR


class DataValidationException(ValidationException):
    """Exception for issues caught while validating user data."""

    _error_code = ErrorCodes.VALIDATION_ERROR


class ForecastingDataException(DataValidationException):
    """Exception related to data being malformed for a forecasting scenario."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.INVALIDFORECASTINGDATA_ERROR


class DataPrepValidationException(DataValidationException):
    """Exception related to dataprep validation service."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.DATAPREPVALIDATION_ERROR


class DataScriptException(DataValidationException):
    """Exception for issues with user's get_data script."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.DATASCRIPT_ERROR


class ScenarioNotSupportedException(ValidationException):
    """Exception for unsupported or unimplemented scenarios."""

    _error_code = ErrorCodes.SCENARIONOTSUPORTED_ERROR


class OptionalDependencyMissingException(ScenarioNotSupportedException):
    """Exception for when an a soft dependency is missing."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.OPTIONALSCENARIONOTENABLED_ERROR


class EarlyTerminationException(UserErrorException):
    """Exception for when user sends an interrupt."""

    _error_code = ErrorCodes.EARLYTERMINATION_ERROR


class AutoMLExperimentException(SystemException):
    """Exception that happens during AutoML runtime."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.EXPERIMENTRUN_ERROR


class PreTrainingException(AutoMLExperimentException):
    """Exception for anything that goes wrong before fitting the user's model."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.PRETRAINING_ERROR


class CacheException(PreTrainingException):
    """Exception for any cache issues."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.CACHE_ERROR


class FeaturizationException(PreTrainingException):
    """Exception for issues that arise during featurization."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.FEATURIZATION_ERROR


class ProblemInfoException(PreTrainingException):
    """Exception for calculating data characteristics."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.PROBLEMINFO_ERROR


class TrainingException(AutoMLExperimentException):
    """Exception for issues that arise during model training."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.TRAINING_ERROR


class MetricCalculationException(TrainingException):
    """Exception for metric not being able to be calculated."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.METRICCALCULATION_ERROR


class ModelFitException(TrainingException):
    """Exception for failure to fit the model."""

    # TODO - define a code for this
    #  _error_code = ErrorCodes.MODELFIT_ERROR


class PostTrainingException(AutoMLExperimentException):
    """Exception for failures after a model has already been fitted."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.POSTTRAINING_ERROR


class ModelExplanationException(PostTrainingException):
    """Exception for failures while trying to explain the model."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.MODELEXPLANATION_ERROR


class OnnxException(PostTrainingException):
    """Exception for failures while trying to run ONNX operations."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.ONNX_ERROR


class DataprepException(ClientException):
    """Exceptions related to Dataprep."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.DATAPREPVALIDATION_ERROR


# TODO this should move to azureml.exceptions
class NotFoundException(ValidationException):
    """Exception for when a resource could not be found."""

    _error_code = ErrorCodes.NOTFOUND_ERROR


class InvalidRunState(ScenarioNotSupportedException):
    """Exception for trying to use a run that is not in a valid state for the given operation."""

    _error_code = ErrorCodes.INVALIDRUNSTATE_ERROR


class ApiInvocationException(ServiceException):
    """Exception is thrown when Api invocation fails."""

    _error_code = ErrorCodes.APIINVOCATION_ERROR
