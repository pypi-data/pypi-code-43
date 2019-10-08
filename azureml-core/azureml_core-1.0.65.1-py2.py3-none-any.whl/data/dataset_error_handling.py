# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Module for dataset error handling in Azure Machine Learning service."""

from azureml.data._dataprep_helper import dataprep, ensure_dataflow


class DatasetValidationError(Exception):
    """Exception class for datasets validation error."""

    def __init__(self, message):
        """Class DatasetValidationError constructor.

        :param message: The error message.
        :type message: str
        """
        super().__init__(message)


class DatasetExecutionError(Exception):
    """Exception class for datasets execution error."""

    def __init__(self, message):
        """Class DatasetExecutionError constructor.

        :param message: The error message.
        :type message: str
        """
        super().__init__(message)


def _validate_has_data(dataflow, error_message):
    ensure_dataflow(dataflow)
    try:
        dataflow.verify_has_data()
    except (dataprep().api.dataflow.DataflowValidationError,
            dataprep().api.errorhandlers.ExecutionError):
        raise DatasetValidationError(error_message)
    except Exception as e:
        raise e


def _validate_has_columns(dataflow, columns, expected_types=None):
    if expected_types is not None and len(columns) != len(expected_types):
        raise ValueError('Length of `columns` and `expected_types` must be the same')
    ensure_dataflow(dataflow)
    profile = dataflow.keep_columns(columns).take(1)._get_profile()
    if profile.row_count == 0 or profile.row_count is None:
        missing_columns = columns
    else:
        missing_columns = [col for col in columns if col not in profile.columns.keys()]
    if missing_columns:
        raise DatasetValidationError('The specified columns {} do not exist in the current dataset.'
                                     .format(missing_columns))
    if not expected_types:
        return
    mismatch_columns = []
    mismatch_types = []
    for i in range(len(columns)):
        if profile.columns[columns[i]].type != expected_types[i]:
            mismatch_columns.append(columns[i])
            mismatch_types.append(str(expected_types[i])[10:])
    if mismatch_columns:
        raise DatasetValidationError('The specified columns {} do not have the expected types {}.'
                                     .format(mismatch_columns, mismatch_types))


def _try_execute(action):
    try:
        return action()
    except Exception as e:
        raise DatasetExecutionError(str(e))
