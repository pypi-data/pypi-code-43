# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Restclient constants"""

BASE_RUN_SOURCE = "azureml.runsource"
SDK_TARGET = "sdk"

# key constant
RUN_ORIGIN = "ExperimentRun"
NOTEBOOK_ORIGIN = "LocalUpload"  # "ExperimentNotebook"
CREATED_FROM_NOTEBOOK_NAME = "Notebook"
ATTRIBUTE_CONTINUATION_TOKEN_NAME = "continuation_token"
ATTRIBUTE_VALUE_NAME = "value"
ACCESS_TOKEN_NAME = "access_token"
CUSTOM_HEADERS_KEY = "custom_headers"
PAGE_SIZE_KEY = "page_size"
TOP_KEY = "top"
ORDER_BY_KEY = "orderby"
CALLER_KEY = "caller"
FILTER_KEY = "filter"
QUERY_PARAMS_KEY = "query_params"
VIEW_TYPE_KEY = "view_type"

# user_agent
RUN_USER_AGENT = "sdk_run"
AUTOML_RUN_USER_AGENT = "sdk_run_automl"
SCRIPT_RUN_USER_AGENT = "sdk_run_script"
HYPER_DRIVE_RUN_USER_AGENT = "sdk_run_hyper_drive"

# size constant
DEFAULT_PAGE_SIZE = 500


# run document statuses
class RunStatus(object):
    # Ordered by transition order
    QUEUED = "Queued"
    PREPARING = "Preparing"
    PROVISIONING = "Provisioning"
    STARTING = "Starting"
    RUNNING = "Running"
    CANCEL_REQUESTED = "CancelRequested"  # Not official yet
    CANCELED = "Canceled"  # Not official yet
    FINALIZING = "Finalizing"
    COMPLETED = "Completed"
    FAILED = "Failed"

    @classmethod
    def list(cls):
        """Return the list of supported run statuses."""
        return [cls.QUEUED, cls.PREPARING, cls.PROVISIONING, cls.STARTING,
                cls.RUNNING, cls.CANCEL_REQUESTED, cls.CANCELED,
                cls.FINALIZING, cls.COMPLETED, cls.FAILED]


class RequestHeaders(object):
    # CALL_NAME = "x-ms-synthetic-source"
    CALL_NAME = "x-ms-caller-name"
    CLIENT_REQUEST_ID = "x-ms-client-request-id"
    CLIENT_SESSION_ID = "x-ms-client-session-id"
    USER_AGENT = "User-Agent"
    CORRELATION_CONTEXT = "correlation-context"
    REQUEST_ID = "request-id"
