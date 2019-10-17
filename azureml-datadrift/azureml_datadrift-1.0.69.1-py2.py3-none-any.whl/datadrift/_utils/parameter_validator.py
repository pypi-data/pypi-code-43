# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Parameter Validator."""

import os
import re
from datetime import datetime

from azureml.core import Workspace
from azureml.data import TabularDataset
from azureml.datadrift import alert_configuration
from azureml.datadrift._utils.constants import FREQUENCY_MONTH, FREQUENCY_WEEK, FREQUENCY_DAY

from .._logging._telemetry_logger import _TelemetryLogger

module_logger = _TelemetryLogger.get_telemetry_logger(__name__)
EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
NAME_REGEX = re.compile(r'^[a-zA-Z0-9][\w\-]{0,35}$')
NAME_ERROR_MSG = "Invalid name: {}. Name must be up to 36 characters long and can only contain alphanumeric " \
                 "characters or - "
FEATURE_NAME_REGEX = re.compile(r'(^([a-zA-Z0-9._][a-zA-Z0-9 ._-]{0,62})[a-zA-Z0-9._-]$|^[a-zA-Z0-9._]$)')


class ParameterValidator:
    @staticmethod
    def validate_workspace(input):
        if not isinstance(input, Workspace):
            raise TypeError("workspace must be a Workspace type")
        return input

    @staticmethod
    def validate_name(input):
        try:
            input = ParameterValidator._validate_str(input)
        except TypeError:
            raise TypeError("name must be a string")
        match = re.match(NAME_REGEX, input)
        if not match:
            raise ValueError(NAME_ERROR_MSG.format(input))
        return input

    @staticmethod
    def validate_dataset(input, none_ok=False):
        if not ((none_ok and input is None) or isinstance(input, TabularDataset)):
            raise TypeError("dataset must be of type TabularDataset")
        return input

    @staticmethod
    def validate_timeseries_dataset(input, none_ok=True):
        input = ParameterValidator.validate_dataset(input, none_ok)
        # TODO: Check trait of Dataset once they've implemented it
        fine, _ = input.timestamp_columns
        if not fine:
            raise TypeError("dataset must be time series, please use with_timestamp_columns()")
        return input

    @staticmethod
    def validate_model_name(input):
        if not isinstance(input, str):
            raise TypeError("model_name must be a string")
        pattern = r'^([a-zA-Z0-9 ._-]*)$'
        if(re.match(pattern, input) is None):
            raise ValueError("model_name should only contain characters, numbers, "
                             "dash, underscore, dot and whitespace.")
        return input

    @staticmethod
    def validate_model_version(input):
        if not isinstance(input, int) or input <= 0:
            raise TypeError("model_version must be a positive integer")
        return input

    @staticmethod
    def validate_services(input, none_ok=False):
        if not (none_ok and not input):
            if not input or not isinstance(input, list):
                raise TypeError("services must be a non-empty list")
        if input:
            for s in input:
                if not isinstance(s, str):
                    raise TypeError("Each service name must be a string")
                pattern = r'^([a-zA-Z0-9 ._-]*)$'
                if (re.match(pattern, s) is None):
                    raise ValueError("service name should only contain characters, numbers, "
                                     "dash, underscore, dot and whitespace.")
        return input

    @staticmethod
    def validate_compute_target_name(input, workspace, none_ok=True, not_exist_ok=False):
        if not ((none_ok and input is None) or isinstance(input, str)):
            raise TypeError("compute_target_name must be a string")
        if input is None:
            return input
        if not not_exist_ok and input not in workspace.compute_targets:
            raise KeyError("compute_target with name {} does not exist".format(input))
        if not not_exist_ok and workspace.compute_targets[input]._compute_type is not "AmlCompute":
            raise TypeError("Compute target {} must be an AmlCompute type".format(input))
        if not not_exist_ok and workspace.compute_targets[input].status.provisioning_state.capitalize() != "Succeeded":
            raise TypeError("Compute target {} must be in active state".format(input))
        return input

    @staticmethod
    def validate_frequency(input, dataset_based=False, none_ok=True):
        frequencies = [FREQUENCY_DAY]
        if dataset_based:
            frequencies.extend([FREQUENCY_WEEK, FREQUENCY_MONTH])
        if not ((none_ok and input is None) or input in frequencies):
            raise TypeError("frequency must one of {}".format(frequencies))
        return input if input else frequencies[0]

    @staticmethod
    def validate_interval(input, none_ok=True, instance_logger=module_logger):
        if not ((none_ok and input is None) or (isinstance(input, int) and input > 0)):
            raise TypeError("interval must be a positive integer")
        if not (input is 1 or input is None):
            instance_logger.warning("Only interval=1 is supported for now, updating..")
        return 1  # TODO: 1 if input is None else input

    @staticmethod
    def validate_datetime(input, name="Input", none_ok=True):
        if not ((none_ok and input is None) or isinstance(input, datetime)):
            raise TypeError("{} must be a datetime".format(name))
        return input

    @staticmethod
    def validate_feature_list(input, none_ok=True):
        if not (none_ok and not input):
            if not isinstance(input, list):
                raise TypeError("feature_list must be a list")
            if len(input) > 200:
                raise ValueError("feature_list exceeds max length of 200")
            for i in input:
                if not isinstance(i, str) or "," in i:
                    raise ValueError("A feature must be a string and cannot contain any commas(,)")
                if not re.match(FEATURE_NAME_REGEX, i):
                    raise ValueError("Feature name should only contain characters, numbers, dashes, underscores, dots "
                                     "and whitespaces.")
        return input

    @staticmethod
    def validate_alert_configuration(input, none_ok=True):
        if not (none_ok and input is None):
            if not isinstance(input, alert_configuration.AlertConfiguration):
                raise TypeError("alert_config must be of type {}".format(
                    alert_configuration.AlertConfiguration.__module__ +
                    alert_configuration.AlertConfiguration.__name__))
            input.email_addresses = ParameterValidator.validate_email_addresses(input.email_addresses)
        return input

    @staticmethod
    def validate_run_id(input):
        try:
            return ParameterValidator._validate_str(input)
        except TypeError:
            raise TypeError("run_id must be a string")

    @staticmethod
    def validate_filepath(input, name="Input", none_ok=True):
        if not ((none_ok and input is None) or isinstance(input, str)):
            raise TypeError("{} must be a datetime".format(name))
        if (input is not None and not os.path.exists(os.path.dirname(input))):
            raise NotADirectoryError("Directory {} does not exist yet.".format(os.path.dirname(input)))
        return input

    @staticmethod
    def is_guid(test_str):
        pattern = r'^([a-zA-Z0-9]{8}-([a-zA-Z0-9]{4}-){3}[a-zA-Z0-9]{12})$'
        matched = re.match(pattern, test_str)
        return (matched is not None)

    @staticmethod
    def validate_drift_threshold(input, none_ok=True):
        if not ((none_ok and input is None) or (isinstance(input, float) and 0 <= input <= 1)):
            raise TypeError("threshold must be a positive float value between 0 and 1")
        return input

    @staticmethod
    def validate_email_addresses(input):
        if not (isinstance(input, list)):
            raise TypeError("email_addresses must be of type list(str)")
        invalid_emails = []
        for m in input:
            match = re.match(EMAIL_REGEX, m)
            if not match:
                invalid_emails.append(m)
        if invalid_emails:
            raise ValueError("Invalid email address format: {}".format(", ".join(invalid_emails)))
        return input

    @staticmethod
    def validate_latency(input, none_ok=True):
        if not ((none_ok and input is None) or (isinstance(input, int))):
            raise TypeError("latency must be of type int")
        if input and input < 0:
            raise ValueError("latency must be greater than or equal to 0")
        return input

    @staticmethod
    def _validate_str(input):
        if not isinstance(input, str):
            raise TypeError("run_id must be a string")
        return input

    @staticmethod
    def validate_start_date_end_date(start_date, end_date, frequency):
        start_date = ParameterValidator.validate_datetime(start_date)
        end_date = ParameterValidator.validate_datetime(end_date)

        if end_date < start_date:
            raise ValueError("Parameter end_date needs to be set after start_date")

        delta = end_date - start_date
        span = 0
        if frequency == FREQUENCY_DAY:
            span = delta.days
        elif frequency == FREQUENCY_WEEK:
            span = delta.days / 7
        elif frequency == FREQUENCY_MONTH:
            _ = (end_date.year - start_date.year) * 12
            span = _ + end_date.month - start_date.month

        if span > 30:
            raise ValueError("Exceeded maximum backfill batch size. Reduce window between start_date and end_date")
        return start_date, end_date
