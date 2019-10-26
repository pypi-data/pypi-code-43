# Copyright (c) Microsoft Corporation. All rights reserved.
# pylint: disable=line-too-long
from ._loggerfactory import session_id
import json
import os

def _get_error_file_path():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, "_errormessages_en-us.json")

with open(_get_error_file_path(), 'rt') as error_messages_file:
    try:
        error_messages = json.load(error_messages_file)
    except Exception:
        error_messages = {}

extra_message_error_codes = ['ConfigurationError', 'ExpressionError', 'StorageError', 'InvalidPath', 'AuthenticationFailure', 'FailedToSendFeather', 'FailedToSendNPZ']

def raise_engine_error(error_response):
    error_code = error_response['errorCode']
    if 'ActivityExecutionFailed' in error_code:
        raise ExecutionError(error_response)
    elif 'UnableToPreviewDataSource' in error_code:
        raise ExecutionError(error_response)
    elif 'EmptySteps' in error_code:
        raise EmptyStepsError()
    elif 'OperationCanceled' in error_code:
        raise OperationCanceled()
    else:
        raise UnexpectedError(error_response)


class DataPrepException(Exception):
    pass


class OperationCanceled(DataPrepException):
    """
    Exception raised when an execution has been canceled.
    """
    def __init__(self):
        super().__init__('The operation has been canceled.')


class ExecutionError(DataPrepException):
    """
    Exception raised when dataflow execution fails.
    """
    def __init__(self, error_response):
        self.error_code = error_response['errorData'].get('errorCode', None)
        self.step_failed = error_response['errorData'].get('stepFailed', None)
        self.root_error = error_response['errorData'].get('rootError', None)
        error_message = error_response['errorData']['errorMessage'] if 'errorMessage' in error_response['errorData'] \
            else error_response['message'] if 'message' in error_response \
            else ''
        message = error_messages.get(self.error_code, '') if self.error_code is not None else ''
        if self.root_error is not None:
            message += 'Root error : {}.'.format(self.root_error)
        if ((self.error_code is None or self.error_code in extra_message_error_codes)
                and error_message is not None and len(error_message) > 0):
            message += '({})'.format(error_message)
        message +='|session_id={}'.format(session_id)
        super().__init__(message if message is not None else error_message)


class EmptyStepsError(DataPrepException):
    """
    Exception raised when there are issues with steps in the dataflow.
    """
    def __init__(self):
        self.error_code = 'PandasImportError'
        super().__init__('The Dataflow contains no steps and cannot be executed. '
                         'Use a reader to create a Dataflow that can load data.')


class UnexpectedError(DataPrepException):
    """
    Unexpected error.

    :var error: Error code of the failure.
    """
    def __init__(self, error):
        self.error_code = 'UnexpectedFailure'
        self.error = error


class PandasImportError(DataPrepException):
    """
    Exception raised when pandas was not able to be imported.
    """
    _message = 'Could not import pandas. Ensure a compatible version is installed by running: pip install azureml-dataprep[pandas]'
    def __init__(self):
        print('PandasImportError: ' + self._message)
        self.error_code = 'PandasImportError'
        super().__init__(self._message)


class NumpyImportError(DataPrepException):
    """
    Exception raised when numpy was not able to be imported.
    """
    _message = 'Could not import numpy. Ensure a compatible version is installed by running: pip install azureml-dataprep[pandas]'
    def __init__(self):
        print('NumpyImportError: ' + self._message)
        self.error_code = 'NumpyImportError'
        super().__init__(self._message)
