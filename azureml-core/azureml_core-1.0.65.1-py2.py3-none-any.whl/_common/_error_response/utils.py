# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
from azureml._common.exceptions import AzureMLException
from azureml._common._error_response import _error_response_constants
import azureml.exceptions
import inspect

EXCEPTION_MODULES = [azureml.exceptions]


def _get_exception(code, message, exception=None):
    for module in EXCEPTION_MODULES:
        for _, azureml_exception in inspect.getmembers(module):
            if getattr(azureml_exception, "_error_code", None) == code:
                return azureml_exception(exception_message=message, inner_exception=exception)
    return None


def _get_codes(error_response_json):
    """Get the list of error codes from an error response json"""
    error_response_json = error_response_json.get("error")
    if error_response_json is None:
        return []
    code = error_response_json.get('code')
    if code is None:
        raise ValueError("Error response does not contain an error code.")
    codes = [code]
    inner_error = error_response_json.get('inner_error')
    while inner_error is not None:
        code = inner_error.get('code')
        if code is None:
            break
        codes.append(code)
        inner_error = inner_error.get('inner_error')
    return codes[::-1]


def error_response_to_exception(error_response):
    """Given an error code, returns the most granular azureml.exception Exception"""
    error_response_json = json.loads(error_response)
    codes = _get_codes(error_response_json)
    # Codes are in reverse order, so starting with most granular, return the first exception you find
    for code in codes:
        exception = _get_exception(code, error_response_json.get('message'))
        if exception is not None:
            return exception
    return azureml.exceptions.AzureMLException(exception_message=error_response_json.get('message'))


def map_non_schema_exception(exception):
    """
    Given an exception that doesn't support the error handling schema
    returns the most granular azureml.exception Exception. If no exception is
    found, returns an AzureMLException.
    """
    error_code = getattr(exception, "_error_code",
                         getattr(exception, "error_code",
                                 getattr(exception, "code", None)))

    return _get_exception(error_code, str(exception), exception) if error_code is not None else None


def code_in_error_response(error_response, error_code):
    """Given an error response, returns whether a code exists in it."""
    error_response_json = json.loads(error_response)
    codes = _get_codes(error_response_json)
    return error_code in codes


def _code_in_hierarchy(leaf_code, target_code):
    """
    Given a leaf node, check if a target code is in the hierarchy. This is limited to hierarchies this
    version of the SDK is aware of.
    """
    for _, hierarchy in vars(_error_response_constants.ErrorHierarchy).items():
        if isinstance(hierarchy, list) and leaf_code in hierarchy:
            return target_code in hierarchy
    return False


def is_error_code(exception, error_code_hierarchy):
    """
    Determine whether an error code is in the exceptions error code hierarchy.
    :param exception: exception to check for error code hierarchy
    :param error_code_hierarchy: The desired code hierarchy as found in
        azureml._common_error_response._error_response_constants.ErrorHierarchy
    :return: bool
    """
    if isinstance(exception, AzureMLException):
        error_response = exception._serialize_json()
        for error_code in error_code_hierarchy:
            if not code_in_error_response(error_response, error_code):
                return False
        return True
    if hasattr(exception, "_error_code"):
        return exception._error_code == error_code_hierarchy
    if hasattr(exception, "error"):
        try:
            error_response = json.loads(str(exception.error))
            for error_code in error_code_hierarchy:
                if not code_in_error_response(json.dumps(error_response), error_code):
                    return False
            return True
        except ValueError:
            pass
    return False
