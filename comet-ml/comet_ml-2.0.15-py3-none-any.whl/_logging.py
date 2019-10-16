# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

"""
Author: Boris Feld

This module contains logging configuration for Comet

"""
import json
import logging
import os
import re
import sys
from copy import copy
from datetime import datetime

import requests

from .config import get_config
from .json_encoder import NestedEncoder
from .utils import get_user

LOGGER = logging.getLogger(__name__)

MSG_FORMAT = "COMET %(levelname)s: %(message)s"
FILE_MSG_FORMAT = "[%(process)d-%(processName)s:%(thread)d] %(relativeCreated)d COMET %(levelname)s [%(filename)s:%(lineno)d]: %(message)s"

GO_TO_DOCS_MSG = " \nFor more details, please refer to: https://www.comet.ml/docs/python-sdk/warnings-errors"

INTERNET_CONNECTION_ERROR = (
    "Failed to establish connection to Comet server. Please check your internet connection. "
    "Your experiment would not be logged" + GO_TO_DOCS_MSG
)

INVALID_WORKSPACE_NAME = "Workspace %s doesn't exist."

INVALID_PROJECT_NAME = "project_name argument can't be empty."

INVALID_API_KEY = (
    "The given api key %s is invalid, please check it against the dashboard. "
    "Your experiment would not be logged" + GO_TO_DOCS_MSG
)

INVALID_REST_API_KEY = (
    "The given REST API key %s is invalid, please check it against the dashboard. "
)

METRIC_ARRAY_WARNING = (
    "Cannot safely convert %r object to a scalar value, using it string"
    " representation for logging."
)

PARSING_ERR_MSG = """We failed to parse your parameter configuration file.

Type casting will be disabled for this run, please fix your configuration file.
"""

CASTING_ERROR_MESSAGE = """Couldn't cast parameter %r, returning raw value instead.
Please report it to comet.ml and use `.raw(%r)` instead of `[%r]` in the meantime."""

LOG_ASSET_FOLDER_ERROR = (
    "We failed to read directory %s for uploading.\n"
    "Please double check the file path, permissions, and that it is a directory"
)

UPLOAD_FILE_OS_ERROR = (
    "We failed to read file %s for uploading.\n"
    "Please double check the file path and permissions"
)

UPLOAD_ASSET_TOO_BIG = "Asset %s is bigger than the upload limit, %s > %s"

LOG_IMAGE_TOO_BIG = "Image %s is bigger than the upload limit, %s > %s"

LOG_FIGURE_TOO_BIG = "Figure number %d is bigger than the upload limit, %s > %s"

LOG_AUDIO_TOO_BIG = "Audio %s is bigger than the upload limit, %s > %s"

NATIVE_STD_WRAPPER_NOT_AVAILABLE = (
    "Native output logging mode is not available, fallbacking on basic output logging"
)

UNKOWN_STD_WRAPPER_SPEC = (
    "Unknown output logging mode: %s, fallbacking on basic output logging"
)

EXPERIMENT_LIVE = "Experiment is live on comet.ml %s\n"

OFFLINE_EXPERIMENT_END = "To upload this offline experiment, run:\n    comet upload %s"

OFFLINE_SENDER_STARTS = "Starting the upload of the experiment"

OFFLINE_SENDER_ENDS = "The offline experiment has been uploaded on comet.ml %s\n"

ADD_TAGS_ERROR = "Failed to add tag(s) %s to the experiment\n"

ADD_SYMLINK_ERROR = "Failed to create symlink to project:%s for experiment\n"

OFFLINE_EXPERIMENT_TEMPORARY_DIRECTORY = (
    "The offline directory %r was not usable.\n"
    "Reason: %r\n"
    "Saving the experiment in directory %s instead."
)

OFFLINE_EXPERIMENT_INVALID_WS_MSG = "An invalid message has been detected"

OFFLINE_EXPERIMENT_INVALID_UPLOAD_MSG = "An invalid upload message has been detected"

EXPERIMENT_INVALID_STEP = "Passed step value %r is not a number, ignoring it"

EXPERIMENT_INVALID_EPOCH = "Passed epoch value %r is not a number, ignoring it"

STREAMER_WAIT_FOR_FINISH_FAILED = (
    "Comet failed to send all the data back (%d messages and %d uploads)"
)

REGISTER_RPC_FAILED = "Failed to register callback named %r"

WS_SSL_ERROR_MSG = (
    "There's seem to be an issue with your system's SSL certificate bundle."
    "This is likely a system wide issue that is not related to Comet."
    "Please see more information here:"
    "https://www.comet.ml/docs/python-sdk/warnings-errors/"
)

OFFLINE_EXPERIMENT_ALREADY_UPLOADED = (
    "Experiment %r was already uploaded, you can re-upload it by using the"
    " --force-reupload flag"
)

SEND_NOTIFICATION_FAILED = (
    "Error sending notification, make sure you have opted-in for notifications"
)

GET_CALLBACK_FAILURE = "Failure to add Comet SDK callback to %s, the run will likely miss parameters and/out metrics"


class TracebackLessFormatter(logging.Formatter):
    def format(self, record):

        if getattr(record, "show_traceback", False) is False:

            # Make a copy of the record to avoid altering it
            new_record = copy(record)

            # And delete exception information so no traceback could be formatted
            # and displayed
            new_record.exc_info = None
            new_record.exc_text = None
        else:
            new_record = record

        return super(TracebackLessFormatter, self).format(new_record)


WS_ON_OPEN_MSG = "WS Socket connection open"

WS_ON_CLOSE_MSG = "WS connection closed"

COMET_DISABLED_AUTO_LOGGING_MSG = "COMET_DISABLE_AUTO_LOGGING is 1; ignoring '%s'"

LOG_DATASET_ERROR = "Failed to create dataset hash"

OS_PACKAGE_MSG_SENDING_ERROR = "Error sending os_packages message, got %d %r"

OPTIMIZER_KWARGS_CONSTRUCTOR_DEPRACETED = "Passing Experiment through Optimizer constructor is deprecated; pass them to Optimizer.get_experiments or Optimizer.next"


def shorten_record_name(record_name):
    """ Return the first part of the record (which can be None, comet or
    comet.connection)
    """
    if record_name is None:
        return record_name

    return record_name.split(".", 1)[0]


class HTTPHandler(logging.Handler):
    def __init__(self, url, api_key, experiment_key):
        super(HTTPHandler, self).__init__()
        self.url = url
        self.api_key = api_key
        self.experiment_key = experiment_key
        self.session = requests.Session()

    def mapLogRecord(self, record):
        return record.__dict__

    def emit(self, record):
        """
        Emit a record.

        Send the record to the Web server as JSON body
        """
        try:
            payload = {
                "apiKey": self.api_key,
                "record": self.mapLogRecord(record),
                "experimentKey": self.experiment_key,
                "levelname": record.levelname,
                "sender": record.name,
                "shortSender": shorten_record_name(record.name),
            }
            body = json.dumps(payload, cls=NestedEncoder)

            response = self.session.post(
                self.url,
                data=body,
                headers={"Content-Type": "application/json;charset=utf-8"},
            )
            response.raise_for_status()
        except Exception:
            self.handleError(record)

    def handleError(self, record):
        # Hide errors to avoid bad interaction with console logging
        pass


def expand_log_file_path(log_file_path):
    """
    Expand patterns in the file logging path.

    Allowed patterns:
        * {datetime}
        * {pid}
        * {project}
        * {user}
    """

    def make_valid(s):
        # type: (str) -> str
        s = str(s).strip().replace(" ", "_")
        return re.sub(r"(?u)[^-\w.]", "", s)

    user = make_valid(get_user())

    patterns = {
        "datetime": datetime.now().strftime("%Y%m%d-%H%M%S"),
        "pid": os.getpid(),
        "project": get_config("comet.project_name") or "general",
        "user": user,
    }
    if log_file_path is not None:
        try:
            return log_file_path.format(**patterns)
        except KeyError:
            LOGGER.info(
                "Invalid logging file pattern: '%s'; ignoring" % log_file_path,
                exc_info=True,
            )
            return log_file_path


def setup(config):
    root = logging.getLogger("comet_ml")
    root.setLevel(logging.DEBUG)

    # Don't send comet-ml to the application logger
    root.propagate = False

    # Add handler for console, basic INFO:
    console = logging.StreamHandler()
    logging_console = config["comet.logging.console"]

    if logging_console and logging_console.upper() in [
        "DEBUG",
        "ERROR",
        "INFO",
        "CRITICAL",
        "FATAL",
        "WARN",
        "WARNING",
    ]:
        console.setLevel(logging_console.upper())
        console.setFormatter(logging.Formatter(MSG_FORMAT))
    else:
        console.setLevel(logging.INFO)
        console.setFormatter(TracebackLessFormatter(MSG_FORMAT))
    root.addHandler(console)

    # The std* logger might conflicts with the logging if a log record is
    # emitted for each WS message as it would results in an infinite loop. To
    # avoid this issue, all log records after the creation of a message should
    # be at a level lower than info as the console handler is set to info
    # level.

    # Add an additional file handler
    log_file_path = expand_log_file_path(config["comet.logging.file"])
    log_file_level = config["comet.logging.file_level"]
    log_file_overwrite = config["comet.logging.file_overwrite"]
    if log_file_path is not None:

        # Overwrite file if comet.logging.file_overwrite:
        if log_file_overwrite:
            file_handler = logging.FileHandler(log_file_path, "w+")
        else:
            file_handler = logging.FileHandler(log_file_path)

        if log_file_level is not None:
            log_file_level = log_file_level.upper()
            file_handler.setLevel(log_file_level)
        else:
            file_handler.setLevel(logging.DEBUG)

        file_handler.setFormatter(logging.Formatter(FILE_MSG_FORMAT))
        root.addHandler(file_handler)


def setup_http_handler(url, api_key, experiment_key):
    root = logging.getLogger("comet_ml")

    http_handler = HTTPHandler(url, api_key, experiment_key)
    http_handler.setLevel(logging.INFO)

    # Remove any other previous HTTPHandlers:
    root.handlers[:] = [
        handler
        for handler in list(root.handlers)
        if not isinstance(handler, HTTPHandler)
    ]

    # Add new HTTPHandler. Only the current experiment should
    # have its logs forwarded to the backend.
    root.addHandler(http_handler)

    return http_handler


ALREADY_IMPORTED_MODULES = set()


def check_module(module):
    """
    Check to see if a module has already been loaded.
    This is an error, unless comet.disable_auto_logging == 1
    """
    if get_config("comet.disable_auto_logging"):
        LOGGER.debug(COMET_DISABLED_AUTO_LOGGING_MSG % module)
    elif module in sys.modules:
        ALREADY_IMPORTED_MODULES.add(module)


def is_module_already_imported(module):
    return module in ALREADY_IMPORTED_MODULES


def _reset_already_imported_modules():
    # Modify the set in place to be sure to keep the same reference every
    # where
    ALREADY_IMPORTED_MODULES.clear()
