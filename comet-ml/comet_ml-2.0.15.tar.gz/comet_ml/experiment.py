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

This module contains comet base Experiment code

"""
from __future__ import print_function

import atexit
import io
import logging
import numbers
import os
import os.path
import shutil
import sys
import tempfile
import traceback
import types
from collections import defaultdict
from contextlib import contextmanager

import six
from six.moves._thread import get_ident

from ._logging import (
    ADD_TAGS_ERROR,
    ALREADY_IMPORTED_MODULES,
    EXPERIMENT_INVALID_EPOCH,
    EXPERIMENT_INVALID_STEP,
    GO_TO_DOCS_MSG,
    LOG_ASSET_FOLDER_ERROR,
    LOG_AUDIO_TOO_BIG,
    LOG_DATASET_ERROR,
    LOG_FIGURE_TOO_BIG,
    LOG_IMAGE_TOO_BIG,
    METRIC_ARRAY_WARNING,
    UPLOAD_ASSET_TOO_BIG,
    UPLOAD_FILE_OS_ERROR,
)
from ._reporting import EXPERIMENT_CREATION_FAILED, GIT_PATCH_GENERATION_FAILED
from ._typing import Dict, Set
from .comet import (
    format_url,
    generate_guid,
    get_cmd_args_dict,
    is_valid_experiment_key,
    save_matplotlib_figure,
)
from .config import (
    DEFAULT_ASSET_UPLOAD_SIZE_LIMIT,
    DEFAULT_UPLOAD_SIZE_LIMIT,
    get_config,
    get_display_summary,
    get_global_experiment,
    set_global_experiment,
)
from .console import get_std_logger
from .cpu_logging import (
    DEFAULT_CPU_MONITOR_INTERVAL,
    CPULoggingThread,
    is_cpu_info_available,
)
from .env_logging import (
    get_caller_source_code,
    get_env_details,
    get_jupyter_source_code,
)
from .exceptions import (
    CometException,
    FileIsTooBig,
    InterruptedExperiment,
    LambdaUnsupported,
    RPCFunctionAlreadyRegistered,
)
from .file_uploader import compress_git_patch
from .gpu_logging import (
    DEFAULT_GPU_MONITOR_INTERVAL,
    GPULoggingThread,
    convert_gpu_details_to_metrics,
    get_gpu_static_info,
    get_initial_gpu_metric,
    is_gpu_details_available,
)
from .messages import Message, OsPackagesMessage, UploadFileMessage
from .rpc import call_remote_function
from .utils import (
    Histogram,
    data_to_fp,
    encode_and_stringify,
    get_file_extension,
    image_data_to_file_like_object,
    is_list_like,
    is_valid_file_path,
    local_timestamp,
    read_unix_packages,
    write_file_like_to_tmp_file,
    write_numpy_array_as_wav,
)

LOGGER = logging.getLogger(__name__)
LOG_ONCE_CACHE = set()  # type: Set[str]

try:
    import numpy
except ImportError:
    LOGGER.warning("numpy not installed; some functionality will be unavailable")
    pass


def check_max_file_size(file_path, max_upload_size, too_big_msg):
    """ Check if a file identified by its file path is bigger than the maximum
    allowed upload size. Raises FileIsTooBig if the file is greater than the
    upload limit.
    """

    # Check the file size before reading it
    try:
        file_size = os.path.getsize(file_path)
        if file_size > max_upload_size:
            raise FileIsTooBig(file_path, file_size, max_upload_size)

    except OSError:
        LOGGER.error(too_big_msg, file_path, exc_info=True)
        raise


class BaseExperiment(object):
    """
    Experiment is a unit of measurable research that defines a single run with some data/parameters/code/results.

    Creating an Experiment object in your code will report a new experiment to your Comet.ml project. Your Experiment
    will automatically track and collect many things and will also allow you to manually report anything.

    You can create multiple objects in one script (such as when looping over multiple hyper parameters).

    """

    def __init__(
        self,
        project_name=None,
        workspace=None,
        log_code=True,
        log_graph=True,
        auto_param_logging=True,
        auto_metric_logging=True,
        parse_args=True,
        auto_output_logging="default",
        log_env_details=True,
        log_git_metadata=True,
        log_git_patch=True,
        disabled=False,
        log_env_gpu=True,
        log_env_host=True,
        display_summary=None,
        log_env_cpu=True,
    ):
        """
        Creates a new experiment on the Comet.ml frontend.
        Args:
            project_name: Optional. Send your experiment to a specific project. Otherwise will be sent to `Uncategorized Experiments`.
                             If project name does not already exists Comet.ml will create a new project.
            workspace: Optional. Attach an experiment to a project that belongs to this workspace
            log_code: Default(True) - allows you to enable/disable code logging
            log_graph: Default(True) - allows you to enable/disable automatic computation graph logging.
            auto_param_logging: Default(True) - allows you to enable/disable hyper parameters logging
            auto_metric_logging: Default(True) - allows you to enable/disable metrics logging
            parse_args: Default(True) - allows you to enable/disable automatic parsing of CLI arguments
            auto_output_logging: Default("default") - allows you to select
                which output logging mode to use. You can pass `"native"`
                which will log all output even when it originated from a C
                native library. You can also pass `"simple"` which will work
                only for output made by Python code. If you want to disable
                automatic output logging, you can pass `False`. The default is
                `"default"` which will detect your environment and deactivate
                the output logging for IPython and Jupyter environment and
                sets `"native"` in the other cases.
            log_env_details: Default(True) - log various environment
                information in order to identify where the script is running
            log_env_gpu: Default(True) - allow you to enable/disable the
                automatic collection of gpu details and metrics (utilization, memory usage etc..).
                `log_env_details` must also be true.
            log_env_cpu: Default(True) - allow you to enable/disable the
                automatic collection of cpu details and metrics (utilization, memory usage etc..).
                `log_env_details` must also be true.
            log_env_host: Default(True) - allow you to enable/disable the
                automatic collection of host information (ip, hostname, python version, user etc...).
                `log_env_details` must also be true.
            log_git_metadata: Default(True) - allow you to enable/disable the
                automatic collection of git details
            log_git_patch: Default(True) - allow you to enable/disable the
                automatic collection of git patch
            display_summary: Default(True) - control whether the summary is
                displayed on the console or not. If disabled, the summary
                notification is still sent.
            disabled: Default(False) - allows you to disable all network
                communication with the Comet.ml backend. It is useful when you
                just needs to works on your machine-learning scripts and need
                to relaunch them several times at a time.
        """
        self.config = get_config()

        self.display_summary = get_display_summary(display_summary, self.config)
        self._summary = {
            "data": {"url": None},
            "uploads": defaultdict(int),
            "other": {},
            "metric": {},
        }
        self._summary_count = {
            "other": defaultdict(int),
            "metric": defaultdict(int),
        }  # type: Dict[str, Dict[str, int]]

        self.project_name = (
            project_name if project_name else self.config["comet.project_name"]
        )

        self.workspace = workspace if workspace else self.config["comet.workspace"]

        self.workspace = workspace

        self.params = {}
        self.metrics = {}
        self.others = {}
        self.tags = set()

        self.log_code = log_code
        self.log_graph = log_graph
        self.auto_param_logging = auto_param_logging
        self.auto_metric_logging = auto_metric_logging
        self.parse_args = parse_args
        ## Default is "native" for regular environments, False for Jupyter:
        if auto_output_logging == "default":
            if self._in_jupyter_environment():
                self.auto_output_logging = False
            elif self._in_ipython_environment():
                self.auto_output_logging = False
            else:
                self.auto_output_logging = "native"
        else:
            self.auto_output_logging = auto_output_logging
        self.log_env_details = log_env_details

        # Deactivate git logging in case the user disabled logging code
        if not self.log_code:
            log_git_metadata = False
            log_git_patch = False

        self.log_git_metadata = log_git_metadata
        self.log_git_patch = log_git_patch
        self.log_env_gpu = log_env_gpu
        self.log_env_cpu = log_env_cpu
        self.log_env_host = log_env_host
        self.disabled = disabled

        if not self.disabled:
            if len(ALREADY_IMPORTED_MODULES) > 0:
                msg = "You must import Comet before these modules: %s" % ", ".join(
                    ALREADY_IMPORTED_MODULES
                )
                raise ImportError(msg)

        # Generate a unique identifier for this experiment.
        self.id = self._get_experiment_key()

        self.alive = False
        self.is_github = False
        self.focus_link = None
        self.upload_limit = DEFAULT_UPLOAD_SIZE_LIMIT
        self.asset_upload_limit = DEFAULT_ASSET_UPLOAD_SIZE_LIMIT
        self.upload_web_asset_url_prefix = None
        self.upload_web_image_url_prefix = None
        self.upload_api_asset_url_prefix = None
        self.upload_api_image_url_prefix = None

        self.streamer = None
        self.logger = None
        self.gpu_thread = None
        self.cpu_thread = None
        self.run_id = None
        self.project_id = None
        self.optimizer = None
        self._predictor = None

        self.main_thread_id = get_ident()

        # If set to True, wrappers should only run the original code
        self.disabled_monkey_patching = False

        # Experiment state
        self.context = None
        self.curr_step = None
        self.curr_epoch = None
        self.filename = None

        self.figure_counter = 0
        self.batch_report_rate = 10

        self.feature_toggles = {}

        # Storage area for use by loggers
        self._storage = defaultdict(dict)

        self._graph_set = False
        self._code_set = False
        self._pending_calls = []

        # Cleanup old experiment before replace it
        previous_experiment = get_global_experiment()
        if previous_experiment is not None and previous_experiment is not self:
            try:
                previous_experiment._on_end(wait=False)
            except Exception:
                LOGGER.debug(
                    "Failing to clean up Experiment %s",
                    previous_experiment.id,
                    exc_info=True,
                )

        set_global_experiment(self)

        self.rpc_callbacks = {}

    def clean(self):
        """ Clean the experiment loggers, useful in case you want to debug
        your scripts with IPDB.
        """
        self._on_end(wait=False)

    def end(self):
        """
        Use to indicate that the experiment is complete. Useful in
        Jupyter environments to signal comel.ml that the experiment
        has ended.

        In Jupyter, this will also upload the commands that created
        the experiment, from the beginning to the end of this
        session. See the Code tab at Comet.ml.
        """
        if self._in_jupyter_environment() and self.log_code:
            source_code = get_jupyter_source_code()
            self.set_code(source_code, overwrite=True)
        self._on_end(wait=True)

    def display(self, clear=False, wait=True, new=0, autoraise=True):
        """
        Show the Comet.ml experiment page in an IFrame in a
        Jupyter notebook or Jupyter lab, OR open a browser
        window or tab.

        For Jupyter environments:

        Args:
            clear: to clear the output area, use clear=True
            wait: to wait for the next displayed item, use
                  wait=True (cuts down on flashing)

        For non-Jupyter environments:

        Args:
            new: open a new browser window if new=1, otherwise re-use
                 existing window/tab
            autoraise: make the browser tab/window active
        """
        if self._in_jupyter_environment():
            from IPython.display import display, IFrame, clear_output

            if clear:
                clear_output(wait=wait)
            display(
                IFrame(src=self._get_experiment_url(), width="100%", height="800px")
            )
        else:
            import webbrowser

            webbrowser.open(self._get_experiment_url(), new=new, autoraise=autoraise)

    def _get_experiment_key(self):
        experiment_key = self.config["comet.experiment_key"]
        if experiment_key is not None:
            if is_valid_experiment_key(experiment_key):
                return experiment_key
            else:
                raise ValueError(
                    "COMET_EXPERIMENT_KEY is invalid: '%s' must be alphanumeric and between 32 and 50 characters"
                    % experiment_key
                )
        else:
            return generate_guid()

    def _on_start(self):
        """ Called when the Experiment is started
        """
        self._mark_as_started()

    def _mark_as_started(self):
        pass

    def _mark_as_ended(self):
        pass

    def _report_summary(self):
        """
        Display to logger a summary of experiment if there
        is anything to report. If not, no summary will be
        shown.
        """

        self._summary["data"]["url"] = self._get_experiment_url()

        notification_summary = {}

        topics = [
            ("Data", "data"),
            ("Metrics [count] (min, max)", "metric"),
            ("Other [count]", "other"),
        ]

        if self._summary["uploads"]:
            topics.append(("Uploads", "uploads"))

        # First show the header
        if self.display_summary:
            LOGGER.info("----------------------------")
            LOGGER.info("Comet.ml Experiment Summary:")

        for description, topic in topics:
            # Skip empty topics
            if not self._summary[topic]:
                continue

            notification_summary_topic = {}
            max_size = 0

            # Show description
            if self.display_summary:
                LOGGER.info("  %s:", description)

            # Use a list of tuple to keep order of insertion. Dict ordering is
            # not guaranteed until Python 3.7
            description_map = []
            max_size = 0

            # Iterate on each key to format it and compute the keys max size
            for key in sorted(self._summary[topic]):
                desc = key

                if self._summary_count.get(topic, {}).get(key, 0) > 1:
                    desc += " [%s]" % self._summary_count[topic][key]

                max_size = max(max_size, len(desc))

                description_map.append((desc, self._summary[topic][key]))
                notification_summary_topic[desc] = str(self._summary[topic][key])

            notification_summary[description] = notification_summary_topic

            # THen show it
            if self.display_summary:
                for desc, value in description_map:
                    LOGGER.info("    %-" + str(max_size) + "s: %s", desc, value)

        if self.display_summary:
            LOGGER.info("----------------------------")

        self.send_notification("Experiment summary", "finished", notification_summary)

    def _log_once_at_level(self, logging_level, message, *args, **kwargs):
        """ Log the given message once at the given level then at the DEBUG level on further calls
        """
        global LOG_ONCE_CACHE

        if message not in LOG_ONCE_CACHE:
            LOG_ONCE_CACHE.add(message)
            LOGGER.log(logging_level, message, *args, **kwargs)
        else:
            LOGGER.debug(message, *args, **kwargs)

    def _on_end(self, wait=True):
        """ Called when the Experiment is replaced by another one or at the
        end of the script
        """
        LOGGER.debug("Experiment on_end called, wait %s", wait)
        if self.alive:
            if self.optimizer is not None:
                LOGGER.debug("optimizer.end() called")
                force_wait = self.optimizer["optimizer"].end(self)
                if force_wait:
                    # Force wait to be true causes all uploads to finish:
                    LOGGER.debug("forcing wait to be True for optimizer")
                    wait = True
            try:
                self._report_summary()
            except Exception:
                LOGGER.debug("Summary not reported", exc_info=True)
        successful_clean = True

        if self.logger is not None:
            LOGGER.debug("Cleaning STDLogger")
            self.logger.clean()

        if self.gpu_thread is not None:
            self.gpu_thread.close()
            if wait is True:
                LOGGER.debug(
                    "GPU THREAD before join; gpu_thread.isAlive = %s",
                    self.gpu_thread.isAlive(),
                )
                self.gpu_thread.join(2)
                LOGGER.debug(
                    "GPU THREAD after join; gpu_thread.isAlive = %s",
                    self.gpu_thread.isAlive(),
                )

        if self.cpu_thread is not None:
            self.cpu_thread.close()
            if wait is True:
                LOGGER.debug(
                    "CPU THREAD before join; cpu_thread.isAlive = %s",
                    self.cpu_thread.isAlive(),
                )
                self.cpu_thread.join(2)
                LOGGER.debug(
                    "CPU THREAD after join; cpu_thread.isAlive = %s",
                    self.cpu_thread.isAlive(),
                )

        if self.streamer is not None:
            LOGGER.debug("Closing streamer")
            self.streamer.close()
            if wait is True:
                successful_clean = self.streamer.wait_for_finish()

        self._mark_as_ended()

        # Mark the experiment as not alive anymore to avoid future new
        # messages
        self.alive = False

        return successful_clean

    def _start(self):
        try:
            self.alive = self._setup_streamer()

            if not self.alive:
                LOGGER.debug("Experiment is not alive, exiting")
                return

            # Register the cleaning method to be called when the script ends
            atexit.register(self._on_end)

        except CometException as exception:
            tb = traceback.format_exc()
            default_log_message = "Run will not be logged" + GO_TO_DOCS_MSG

            exc_log_message = getattr(exception, "log_message", None)
            exc_args = getattr(exception, "args", None)
            log_message = None
            if exc_log_message is not None and exc_args is not None:
                try:
                    log_message = exc_log_message % exc_args
                except TypeError:
                    pass

            if log_message is None:
                log_message = default_log_message

            LOGGER.error(log_message, exc_info=True)
            self._report(event_name=EXPERIMENT_CREATION_FAILED, err_msg=tb)
            return None
        except Exception:
            tb = traceback.format_exc()
            err_msg = "Run will not be logged" + GO_TO_DOCS_MSG
            LOGGER.error(err_msg, exc_info=True, extra={"show_traceback": True})
            self._report(event_name=EXPERIMENT_CREATION_FAILED, err_msg=tb)
            return None

        # After the handshake is done, mark the experiment as alive
        self._on_start()

        try:
            self._setup_std_logger()
        except Exception:
            LOGGER.error("Failed to setup the std logger", exc_info=True)

        ##############################################################
        ## log_code:
        ##############################################################
        if self.log_code:
            try:
                filename = self._get_filename()
                self.set_filename(filename)
            except Exception:
                LOGGER.error("Failed to set run file name", exc_info=True)
            try:
                self.set_code(self._get_source_code())
            except Exception:
                LOGGER.error("Failed to set run source code", exc_info=True)

        ##############################################################
        ## log_env_details:
        ##############################################################
        if self.log_env_details:
            try:
                self.set_pip_packages()
            except Exception:
                LOGGER.error("Failed to set run pip packages", exc_info=True)
            try:
                self.set_os_packages()
            except Exception:
                LOGGER.error("Failed to set run os packages", exc_info=True)

            try:
                if self.log_env_host:
                    self._log_env_details()
            except Exception:
                LOGGER.error("Failed to log environment details", exc_info=True)

            try:
                if self.log_env_gpu:
                    if is_gpu_details_available():
                        self._start_gpu_thread()
                    else:
                        LOGGER.debug(
                            "GPU details unavailable, don't start the GPU thread"
                        )
            except Exception:
                LOGGER.error("Failed to start the GPU tracking thread", exc_info=True)

            try:
                if self.log_env_cpu:
                    if is_cpu_info_available():
                        self._start_cpu_thread()
                    else:
                        LOGGER.debug(
                            "CPU details unavailable, don't start the CPU thread"
                        )
            except Exception:
                LOGGER.error("Failed to start the CPU tracking thread", exc_info=True)

            try:
                if self.log_git_metadata:
                    self.set_git_metadata()
            except Exception:
                LOGGER.error("Failed to log git metadata", exc_info=True)

            try:
                if self.log_git_patch:
                    self._upload_git_patch()
            except Exception:
                LOGGER.error("Failed to log git patch", exc_info=True)
                tb = traceback.format_exc()
                self._report(event_name=GIT_PATCH_GENERATION_FAILED, err_msg=tb)
                LOGGER.error("Failed to log git patch", exc_info=True)

        ##############################################################
        ## parse_args:
        ##############################################################
        if self.parse_args:
            try:
                self.set_cmd_args()
            except Exception:
                LOGGER.error("Failed to set run cmd args", exc_info=True)

    def _report(self, *args, **kwargs):
        """ Do nothing, could be overridden by subclasses
        """
        pass

    def _setup_streamer(self):
        """
        Do the necessary work to create mandatory objects, like the streamer
        and feature flags
        """
        raise NotImplementedError()

    def _setup_std_logger(self):
        # Override default sys.stdout and feed to streamer.
        self.logger = get_std_logger(self.auto_output_logging, self.streamer)
        if self.logger is not None:
            self.logger.set_experiment(self)

    def _create_message(self, include_context=True):
        # type: (bool) -> Message
        """
        Utility wrapper around the Message() constructor
        Returns: Message() object.

        """
        # First check for pending callbacks call.
        # We do the check in _create_message as it is the most central code
        if get_ident() == self.main_thread_id:
            self._check_rpc_callbacks()

        if include_context is True:
            context = self.context
        else:
            context = None

        return Message(context=context)

    def get_metric(self, name):
        return self.metrics[name]

    def get_parameter(self, name):
        return self.params[name]

    def get_other(self, name):
        return self.others[name]

    def get_key(self):
        """
        Returns the experiment key, useful for using with the ExistingExperiment class
        Returns: Experiment Key (String)
        """
        return self.id

    def log_other(self, key, value):
        """
        Reports a key and value to the `Other` tab on
        Comet.ml. Useful for reporting datasets attributes, datasets
        path, unique identifiers etc.

        See related methods: [`log_parameter`](#experimentlog_parameter) and
            [`log_metric`](#experimentlog_parameter)

        Args:
            key: Any type of key (str,int,float..)
            value: Any type of value (str,int,float..)

        Returns: None
        """
        if self.alive:
            self._summary["other"][self._summary_name(key)] = value
            self._summary_count["other"][self._summary_name(key)] += 1
            message = self._create_message()
            message.set_log_other(key, value)
            self.streamer.put_messge_in_q(message)
            self.others[key] = value

    def log_others(self, dictionary):
        """
        Reports dictionary of key/values to the `Other` tab on
        Comet.ml. Useful for reporting datasets attributes, datasets
        path, unique identifiers etc.

        See [`log_other`](#experimentlog_other)

        Args:
            key: dict of key/values where value is Any type of
                value (str,int,float..)

        Returns: None
        """
        if self.alive:
            if not isinstance(dictionary, dict):
                LOGGER.error(
                    "log_other requires a dict or key/value but not both", exc_info=True
                )
                return
            else:
                for other in dictionary:
                    self.log_other(other, dictionary[other])

    def _summary_name(self, name):
        """
        If in a context manager, add the context name.
        """
        if self.context is not None:
            return "%s_%s" % (self.context, name)
        else:
            return name

    def log_dependency(self, name, version):
        """
        Reports name,version to the `Installed Packages` tab on Comet.ml. Useful to track dependencies.
        Args:
            name: Any type of key (str,int,float..)
            version: Any type of value (str,int,float..)

        Returns: None

        """
        if self.alive:
            message = self._create_message()
            message.set_log_dependency(name, version)
            self.streamer.put_messge_in_q(message)

    def log_system_info(self, key, value):
        """
        Reports key,value to the `System Metric` tab on Comet.ml. Useful to track general system information.
        This information would only show on the table as custom plots are not support for this tab.
        Args:
            key: Any type of key (str,int,float..)
            value: Any type of value (str,int,float..)

        Returns: None

        """
        if self.alive:
            message = self._create_message()
            message.set_system_info(key, value)
            self.streamer.put_messge_in_q(message)

    def log_html(self, html, clear=False):
        """
        Reports any HTML blob to the `HTML` tab on Comet.ml. Useful for creating your own rich reports.
        The HTML will be rendered as an Iframe. Inline CSS/JS supported.
        Args:
            html: Any html string. for example:
            clear: Default to False. when setting clear=True it will remove all previous html.
            ```
            experiment.log_html('<a href="www.comet.ml"> I love Comet.ml </a>')
            ```

        Returns: None

        """
        if self.alive:
            message = self._create_message()
            if clear:
                message.set_htmlOverride(html)
            else:
                message.set_html(html)
            self.streamer.put_messge_in_q(message)

    def log_html_url(self, url, text=None, label=None):
        """
        Easy to use method to add a link to a URL in the `HTML` tab
        on Comet.ml.

        Args:
            url: a link to a file or notebook, for example
            text: text to use a clickable word or phrase (optional; uses url if not given)
            label: text that precedes the link

        Examples:

        >>> experiment.log_html_url("https://my-company.com/file.txt")

        Adds html similar to:

        <a href="https://my-company.com/file.txt">https://my-company.com/file.txt</a>

        >>> experiment.log_html_url("https://my-company.com/file.txt", "File")

        Adds html similar to:

        <a href="https://my-company.com/file.txt">File</a>

        >>> experiment.log_html_url("https://my-company.com/file.txt", "File", "Label")

        Adds html similar to:

        Label: <a href="https://my-company.com/file.txt">File</a>

        """
        text = text if text is not None else url
        if label:
            self.log_html(
                """<div><b>%s</b>: <a href="%s" target="_blank">%s</a></div>"""
                % (label, url, text)
            )
        else:
            self.log_html(
                """<div><a href="%s" target="_blank">%s</a></div>""" % (url, text)
            )

    def set_step(self, step):
        """
        Sets the current step in the training process. In Deep Learning each
        step is after feeding a single batch into the network. This is used to
        generate correct plots on Comet.ml. You can also pass the step directly
        when reporting [log_metric](#experimentlog_metric), and
        [log_parameter](#experimentlog_parameter).

        Args: step: Integer value

        Returns: None

        """

        if step is not None:
            # Support numpy types
            try:
                if isinstance(step, numpy.number):
                    step = step.item()
            except Exception:
                LOGGER.debug("Error converting numpy step", exc_info=True)

            if isinstance(step, numbers.Number):
                self.curr_step = step
                self.log_parameter("curr_step", step)
            else:
                LOGGER.warning(EXPERIMENT_INVALID_STEP, step)

    def set_epoch(self, epoch):
        """
        Sets the current epoch in the training process. In Deep Learning each
        epoch is an iteration over the entire dataset provided. This is used to
        generate plots on comet.ml. You can also pass the epoch
        directly when reporting [log_metric](#experimentlog_metric).

        Args:
            epoch: Integer value

        Returns: None
        """

        if epoch is not None:
            # Support numpy types
            try:
                if isinstance(epoch, numpy.number):
                    epoch = epoch.item()
            except Exception:
                LOGGER.debug("Error converting numpy epoch", exc_info=True)

            if isinstance(epoch, six.integer_types):
                self.curr_epoch = epoch
                self.log_parameter("curr_epoch", epoch)
            else:
                LOGGER.warning(EXPERIMENT_INVALID_EPOCH, epoch)

    def log_epoch_end(self, epoch_cnt, step=None):
        """
        Logs that the epoch finished. Required for progress bars.

        Args:
            epoch_cnt: integer

        Returns: None

        """
        self.set_step(step)

        if self.alive:
            self._summary_count["other"][self._summary_name("step")] += 1
            if step is not None:
                self._summary["metric"][self._summary_name("step")] = step

            self.set_epoch(epoch_cnt)

    def log_metric(self, name, value, step=None, epoch=None, include_context=True):
        """
        Logs a general metric (i.e accuracy, f1).

        e.g.
        ```
        y_pred_train = model.predict(X_train)
        acc = compute_accuracy(y_pred_train, y_train)
        experiment.log_metric("accuracy", acc)
        ```

        See also [`log_metrics`](#experimentlog_metrics)


        Args:
            name: String - name of your metric
            value: Float/Integer/Boolean/String
            step: Optional. Used as the X axis when plotting on comet.ml
            epoch: Optional. Used as the X axis when plotting on comet.ml
            include_context: Optional. If set to True (the default), the
                current context will be logged along the metric.

        Returns: None

        Down sampling metrics:
        Comet guarantees to store 15,000 data points for each metric. If more than 15,000 data points are reported we
        perform a form of reservoir sub sampling - https://en.wikipedia.org/wiki/Reservoir_sampling.

        """
        LOGGER.debug("Log metric: %s %r %r", name, value, step)

        if hasattr(step, "numpy"):
            step = step.numpy()

        if hasattr(epoch, "numpy"):
            epoch = epoch.numpy()

        self.set_step(step)
        self.set_epoch(epoch)

        if self.alive:
            message = self._create_message(include_context=include_context)

            if hasattr(value, "numpy"):
                value = value.numpy()

            if is_list_like(value):
                # Try to get the first value of the Array
                try:
                    if len(value) != 1:
                        raise TypeError()

                    if not isinstance(
                        value[0], (six.integer_types, float, six.string_types, bool)
                    ):
                        raise TypeError()

                    value = value[0]

                except (TypeError):
                    LOGGER.warning(METRIC_ARRAY_WARNING, value)
                    value = str(value)

            if self._predictor:
                if self._summary_name(name) == self._predictor.loss_name:
                    LOGGER.debug(
                        "Reported loss to predictor: %s=%s",
                        self._predictor.loss_name,
                        value,
                    )
                    self._predictor.report_loss(value, self.curr_step)
            self._summary_metric(self._summary_name(name), value)
            message.set_metric(name, value, self.curr_step, self.curr_epoch)
            self.streamer.put_messge_in_q(message)

        # save state.
        self.metrics[name] = value

    def _summary_metric(self, name, value):
        # Keep track on how many time we saw this metric
        self._summary_count["metric"][name] += 1

        # Try to convert value to float
        try:
            value = float(value)
        except Exception:
            pass

        # Process non-float values
        if not isinstance(value, float):
            self._summary["metric"][name] = value
            return

        # For float values, we store min and max values too
        if name in self._summary["metric"]:
            minmax = self._summary["metric"][name]
            if len(minmax) == 2:
                self._summary["metric"][name] = (
                    min(minmax[0], value),
                    max(minmax[1], value),
                )
            else:
                # TODO: We should check in which cases we get in this case and
                # get rid of this
                self._summary["metric"][name] = value
        else:
            self._summary["metric"][name] = (value, value)

    def log_parameter(self, name, value, step=None):
        """
        Logs a single hyperparameter. For additional values that are not hyper parameters it's encouraged to use [log_other](#experimentlog_other).

        See also [`log_parameters`](#experimentlog_parameters).

        If the same key is reported multiple times only the last reported value will be saved.


        Args:
            name: String - name of your parameter
            value: Float/Integer/Boolean/String/List
            step: Optional. Used as the X axis when plotting on Comet.ml

        Returns: None

        """
        if hasattr(step, "numpy"):
            step = step.numpy()

        self.set_step(step)

        if name in self.params and self.params[name] == value:
            return

        if self.alive:
            message = self._create_message()

            if hasattr(value, "numpy"):
                value = value.numpy()

            # Check if we have a list-like object or a string
            if is_list_like(value):
                message.set_params(name, value, self.curr_step)
            else:
                message.set_param(name, value, self.curr_step)

            self.streamer.put_messge_in_q(message)

        self.params[name] = value

    def log_figure(self, figure_name=None, figure=None, overwrite=False, step=None):
        """
        Logs the global Pyplot figure or the passed one and upload its svg
        version to the backend.

        Args:
            figure_name: Optional. String - name of the figure
            figure: Optional. The figure you want to log. If not set, the global
                pyplot figure will be logged and uploaded
            overwrite: Optional. Boolean - if another figure with the same name
                exists, it will be overwritten if overwrite is set to True.
            step: Optional. Used to associate the audio asset to a specific step.
        """
        if self.alive is False:
            return

        self.set_step(step)

        try:
            filename = save_matplotlib_figure(figure)
        except Exception:
            LOGGER.warning("Failing to save the matplotlib figure", exc_info=True)
            # An error occurred
            return

        # Pass additional url params
        figure_number = self.figure_counter
        figure_id = generate_guid()
        url_params = {
            "step": self.curr_step,
            "figCounter": figure_number,
            "context": self.context,
            "runId": self.run_id,
            "overwrite": overwrite,
            "imageId": figure_id,
        }

        if figure_name is not None:
            url_params["figName"] = figure_name

        success = self._upload_file_by_path(
            filename,
            "visualization",
            self.upload_limit,
            url_params,
            LOG_FIGURE_TOO_BIG,
            copy_to_tmp=False,
            error_message_identifier=figure_number,
        )

        if not success:
            return

        self._summary["uploads"]["figures"] += 1
        self.figure_counter += 1

        return self._get_uploaded_figure_url(figure_id)

    def log_asset_data(self, data, file_name=None, overwrite=False, step=None):
        """
        Logs the data given (str, binary, or JSON).

        Args:
            data: data to be saved as asset
            file_name: String - Optional. A custom file name to be displayed
               If not provided the filename from the temporary saved file will be used.
            overwrite: Boolean. Default False. If True will overwrite all existing
               assets with the same name.
            step: Optional. Used to associate the asset to a specific step.

        See also: `APIExperiment.get_experiment_asset(return_type="json")`
        """
        return self._log_asset_data(
            data,
            file_name=file_name,
            overwrite=overwrite,
            asset_type="asset",
            step=step,
        )

    def _log_asset_data(
        self,
        data,
        file_name=None,
        overwrite=False,
        asset_type="asset",
        step=None,
        require_step=False,
    ):
        self.set_step(step)
        try:
            fp = data_to_fp(data)
        except Exception:
            LOGGER.error("Failed to log asset data", exc_info=True)
            return

        if fp is not None:
            return self._log_asset(
                file_data=fp,
                file_name=file_name,
                overwrite=overwrite,
                asset_type=asset_type,
                step=step,
                require_step=require_step,
            )

    def log_asset_folder(self, folder, step=None):
        """
        Logs all the files located in the given folder as assets

        Args:
            folder: String - the path to the folder you want to log
            step: Optional. Used to associate the asset to a specific step.
        """

        self.set_step(step)

        try:
            file_names = sorted(os.listdir(folder))
        except OSError:
            LOGGER.error(LOG_ASSET_FOLDER_ERROR, folder, exc_info=True)
            return

        urls = []

        for file_name in file_names:
            file_path = os.path.join(folder, file_name)

            if os.path.isfile(file_path):
                asset_url = self.log_asset(file_data=file_path)
                urls.append((file_name, asset_url))

        return urls

    def log_asset(
        self,
        file_data,
        file_name=None,
        overwrite=False,
        copy_to_tmp=True,  # if file_data is a file pointer
        step=None,
    ):
        """
        Logs the Asset determined by file_data.

        Args:
            file_data: String or File-like - either the file path of the file you want
                to log, or a file-like asset.
            file_name: String - Optional. A custom file name to be displayed. If not
                provided the filename from the `file_data` argument will be used.
            overwrite: if True will overwrite all existing assets with the same name.
            copy_to_tmp: If `file_data` is a file-like object, then this flag determines
                if the file is first copied to a temporary file before upload. If
                `copy_to_tmp` is False, then it is sent directly to the cloud.
            step: Optional. Used to associate the asset to a specific step.

        Examples:

            >>> experiment.log_asset("model1.h5")

            >>> fp = open("model2.h5", "rb")
            >>> experiment.log_asset(fp,
            ...                      file_name="model2.h5")
            >>> fp.close()

            >>> fp = open("model3.h5", "rb")
            >>> experiment.log_asset(fp,
            ...                      file_name="model3.h5",
            ...                      copy_to_tmp=False)
            >>> fp.close()
        """
        return self._log_asset(
            file_data,
            file_name=file_name,
            overwrite=overwrite,
            copy_to_tmp=copy_to_tmp,
            asset_type="asset",
            step=step,
        )

    def _log_asset(
        self,
        file_data,
        file_name=None,
        overwrite=False,
        copy_to_tmp=True,
        asset_type="asset",
        step=None,
        require_step=False,
    ):
        if self.alive is False:
            return

        if file_data is None:
            raise TypeError("file_data cannot be None")

        self.set_step(step)

        if require_step:
            if self.curr_step is None:
                err_msg = (
                    "Step is mandatory.\n It can either be passed on "
                    "most log methods, set manually with set_step method or "
                    "set automatically through auto-logging integrations"
                )
                raise TypeError(err_msg)

        asset_id = generate_guid()
        url_params = {
            "assetId": asset_id,
            "context": self.context,
            "fileName": file_name,
            "overwrite": overwrite,
            "runId": self.run_id,
            "step": self.curr_step,
        }

        # If the asset type is more specific, include the
        # asset type as "type" in query parameters:
        if asset_type != "asset":
            url_params["type"] = asset_type

        isfile = is_valid_file_path(file_data)

        # Detect invalid file paths
        if not isfile and isinstance(file_data, (six.string_types, bytes)):
            LOGGER.error(UPLOAD_FILE_OS_ERROR, file_data)
            return

        if isfile:
            if url_params["fileName"] is None:
                url_params["fileName"] = os.path.basename(file_data)

            url_params["extension"] = get_file_extension(file_data)

            success = self._upload_file_by_path(
                file_data,
                asset_type,
                self.asset_upload_limit,
                url_params,
                UPLOAD_ASSET_TOO_BIG,
                copy_to_tmp=True,
            )  # copy_to_tmp in order to makes a copy before uploading and removing it

            if not success:
                return
        else:
            self._set_extension_url_parameter(file_name, url_params)

            success = self._upload_file_like(
                file_data,
                asset_type,
                self.asset_upload_limit,
                url_params,
                UPLOAD_ASSET_TOO_BIG,
                copy_to_tmp,
            )

            if not success:
                return

        self._summary["uploads"][asset_type] += 1
        return self._get_uploaded_asset_url(asset_id)

    def log_audio(
        self,
        audio_data,
        sample_rate=None,
        file_name=None,
        metadata=None,
        overwrite=False,
        copy_to_tmp=True,
        step=None,
    ):
        """
        Logs the audio Asset determined by audio data.

        Args:
            audio_data: String or a numpy array - either the file path of the file you want
                to log, or a numpy array given to `scipy.io.wavfile.write` for wav conversion.
            sample_rate: Integer - Optional. The sampling rate given to
                `scipy.io.wavfile.write` for creating the wav file.
            file_name: String - Optional. A custom file name to be displayed.
                If not provided, the filename from the `audio_data` argument
                will be used.
            metadata: Some additional data to attach to the the audio asset.
                Must be JSON-encodable.
            overwrite: if True will overwrite all existing assets with the same name.
            copy_to_tmp: If `audio_data` is a numpy array, then this flag
                determines if the WAV file is first copied to a temporary file
                before upload. If `copy_to_tmp` is False, then it is sent
                directly to the cloud.
            step: Optional. Used to associate the audio asset to a specific step.
        """
        if self.alive is False:
            return

        if audio_data is None:
            raise TypeError("audio_data cannot be None")

        self.set_step(step)

        if metadata is None:
            metadata = {}

        asset_id = generate_guid()
        url_params = {
            "step": self.curr_step,
            "context": self.context,
            "fileName": file_name,
            "runId": self.run_id,
            "overwrite": overwrite,
            "assetId": asset_id,
            "type": "audio",
        }

        # Add the sample rate to the metadata
        if sample_rate is not None:
            metadata["sample_rate"] = sample_rate

        metadata_encoded = encode_and_stringify(metadata)
        if metadata_encoded is not None:
            url_params["metadata"] = metadata_encoded

        isfile = is_valid_file_path(audio_data)

        if isfile:
            if url_params["fileName"] is None:
                url_params["fileName"] = os.path.basename(audio_data)

            url_params["extension"] = get_file_extension(audio_data)

            # The file has not been sampled
            url_params["sampleRate"] = None

            success = self._upload_file_by_path(
                audio_data,
                "audio",
                self.asset_upload_limit,  # TODO: Should we have a separate size limit for Audio?
                url_params,
                LOG_AUDIO_TOO_BIG,
                copy_to_tmp=True,
            )  # copy_to_tmp in order to makes a copy before uploading and removing it
        else:
            self._set_extension_url_parameter(file_name, url_params)

            # Send the sampling rate to the backend
            url_params["sampleRate"] = sample_rate

            if sample_rate is None:
                raise TypeError("sample_rate cannot be None when logging a numpy array")

            if not sample_rate:
                raise TypeError("sample_rate cannot be 0 when logging a numpy array")

            if copy_to_tmp:
                tmpfile = tempfile.NamedTemporaryFile(delete=False)

                write_numpy_array_as_wav(audio_data, sample_rate, tmpfile)

                success = self._upload_file_by_path(
                    tmpfile.name,
                    "audio",
                    self.asset_upload_limit,  # TODO: Should we have a separate size limit for Audio?
                    url_params,
                    LOG_AUDIO_TOO_BIG,
                    copy_to_tmp=False,
                    clean=True,
                )
            else:
                fp = io.BytesIO()

                write_numpy_array_as_wav(audio_data, sample_rate, fp)

                success = self._upload_file_like(
                    fp,
                    "audio",
                    self.asset_upload_limit,  # TODO: Should we have a separate size limit for Audio?
                    url_params,
                    LOG_AUDIO_TOO_BIG,
                    copy_to_tmp=copy_to_tmp,
                )

        if not success:
            return

        self._summary["uploads"]["audio"] += 1
        return self._get_uploaded_asset_url(asset_id)

    def _upload_file_by_path(
        self,
        file_path,
        upload_type,
        max_size,
        url_params,
        too_big_log_msg,
        copy_to_tmp,
        error_message_identifier=None,
        clean=None,
    ):
        try:
            check_max_file_size(file_path, max_size, UPLOAD_FILE_OS_ERROR)
        except FileIsTooBig as exc:
            if error_message_identifier is None:
                error_message_identifier = exc.file_path

            LOGGER.error(
                too_big_log_msg, error_message_identifier, exc.file_size, exc.max_size
            )
            return False
        except Exception:
            LOGGER.debug("Error while checking the file size", exc_info=True)
            return False

        return self._file_upload(
            file_path, upload_type, url_params, copy_to_tmp=copy_to_tmp, clean=clean
        )

    def _upload_file_like(
        self, file_data, upload_type, max_size, url_params, too_big_log_msg, copy_to_tmp
    ):
        if copy_to_tmp:
            # Convert the file-like to a temporary file on disk
            file_path = write_file_like_to_tmp_file(file_data)
            copy_to_tmp = False

            # Todo it would be easier to use the same field name for a file or a figure upload
            if "fileName" in url_params and url_params["fileName"] is None:
                url_params["fileName"] = os.path.basename(file_path)

            if "figName" in url_params and url_params["figName"] is None:
                url_params["figName"] = os.path.basename(file_path)

            return self._upload_file_by_path(
                file_path,
                upload_type,
                max_size,
                url_params,
                too_big_log_msg,
                copy_to_tmp,
                clean=True,
            )

        return self._file_upload(
            file_data, upload_type, url_params, copy_to_tmp=copy_to_tmp
        )

    def log_histogram_3d(self, values, name=None, step=None, **kwargs):
        """
        Logs a histogram of values for a 3D chart as an asset for this
        experiment. Calling this method multiple times with the same
        name and incremented steps will add additional histograms to
        the 3D chart on Comet.ml.

        Args:
            values: a list, tuple, array (any shape) to summarize, or a
                Histogram object
            name: str (optional), name of summary
            step: Optional. Used as the Z axis when plotting on Comet.ml.
            kwargs: Optional. Additional keyword arguments for histogram.

        Note:
            This method requires that step is either given here, or has
            been set elsewhere. For example, if you are using an auto-
            logger that sets step then you don't need to set it here.
        """
        if isinstance(values, Histogram):
            histogram = values
        else:
            histogram = Histogram(**kwargs)
            histogram.add(values)
        if name is None:
            name = "histogram_3d.json"

        return self._log_asset_data(
            histogram.to_json(),
            file_name=name,
            overwrite=False,
            asset_type="histogram3d",
            step=step,
            require_step=True,
        )

    def log_image(
        self,
        image_data,
        name=None,
        overwrite=False,
        image_format="png",
        image_scale=1.0,
        image_shape=None,
        image_colormap=None,
        image_minmax=None,
        image_channels="last",
        copy_to_tmp=True,  # if image_data is a file pointer
        step=None,
    ):
        """
        Logs the image. Images are displayed on the Graphics tab on
        Comet.ml.

        Args:
            image_data: Required. image_data is one of the following:
                - a path (string) to an image
                - a file-like object containing an image
                - a numpy matrix
                - a TensorFlow tensor
                - a PyTorch tensor
                - a list or tuple of values
                - a PIL Image
            name: String - Optional. A custom name to be displayed on the dashboard.
                If not provided the filename from the `image_data` argument will be
                used if it is a path.
            overwrite: Optional. Boolean - If another image with the same name
                exists, it will be overwritten if overwrite is set to True.
            image_format: Optional. String. Default: 'png'. If the image_data is
                actually something that can be turned into an image, this is the
                format used. Typical values include 'png' and 'jpg'.
            image_scale: Optional. Float. Default: 1.0. If the image_data is actually
                something that can be turned into an image, this will be the new
                scale of the image.
            image_shape: Optional. Tuple. Default: None. If the image_data is actually
                something that can be turned into an image, this is the new shape
                of the array. Dimensions are (width, height).
            image_colormap: Optional. String. If the image_data is actually something
                that can be turned into an image, this is the colormap used to
                colorize the matrix.
            image_minmax: Optional. (Number, Number). If the image_data is actually
                something that can be turned into an image, this is the (min, max)
                used to scale the values. Otherwise, the image is autoscaled between
                (array.min, array.max).
            image_channels: Optional. Default 'last'. If the image_data is
                actually something that can be turned into an image, this is the
                setting that indicates where the color information is in the format
                of the 2D data. 'last' indicates that the data is in (rows, columns,
                channels) where 'first' indicates (channels, rows, columns).
            copy_to_tmp: If `image_data` is not a file path, then this flag determines
                if the image is first copied to a temporary file before upload. If
                `copy_to_tmp` is False, then it is sent directly to the cloud.
            step: Optional. Used to associate the audio asset to a specific step.

        """
        if self.alive is False:
            return

        self.set_step(step)

        if image_data is None:
            raise TypeError("image_data cannot be None")

        # Prepare parameters
        figure_number = self.figure_counter

        image_id = generate_guid()
        url_params = {
            "step": self.curr_step,
            "context": self.context,
            "runId": self.run_id,
            "figName": name,
            "figCounter": figure_number,
            "overwrite": overwrite,
            "imageId": image_id,
        }

        isfile = is_valid_file_path(image_data)

        # Detect invalid file paths
        if not isfile and isinstance(image_data, (six.string_types, bytes)):
            LOGGER.error(UPLOAD_FILE_OS_ERROR, image_data)
            return

        if isfile:
            # Take the filename as a figure name if it wasn't provided, here
            # we know that image_data is a valid file_path
            if url_params["figName"] is None:
                url_params["figName"] = os.path.basename(image_data)

            url_params["extension"] = get_file_extension(image_data)

            success = self._upload_file_by_path(
                image_data,
                "visualization",
                self.upload_limit,
                url_params,
                LOG_IMAGE_TOO_BIG,
                copy_to_tmp=copy_to_tmp,
            )

            if not success:
                return
        else:
            self._set_extension_url_parameter(name, url_params)

            try:
                image_object = image_data_to_file_like_object(
                    image_data,
                    name,
                    image_format,
                    image_scale,
                    image_shape,
                    image_colormap,
                    image_minmax,
                    image_channels,
                )
            except Exception:
                LOGGER.error(
                    "Could not convert image_data into an image; ignored", exc_info=True
                )
                return

            success = self._upload_file_like(
                image_object,
                "visualization",
                self.upload_limit,
                url_params,
                LOG_IMAGE_TOO_BIG,
                copy_to_tmp=copy_to_tmp,
            )

            if not success:
                return

        self._summary["uploads"]["images"] += 1
        self.figure_counter += 1

        return self._get_uploaded_image_url(image_id)

    def _set_extension_url_parameter(self, name, url_params):
        extension = get_file_extension(name)
        if extension is not None:
            url_params["extension"] = extension

    def log_current_epoch(self, value):
        """
        Deprecated.
        """
        if self.alive:
            self._summary["metric"][self._summary_name("curr_epoch")] = value
            self._summary_count["metric"][self._summary_name("curr_epoch")] += 1
            message = self._create_message()
            message.set_metric("curr_epoch", value)
            self.streamer.put_messge_in_q(message)

    def log_parameters(self, dic, prefix=None, step=None):
        """
        Logs a dictionary of multiple parameters.
        See also [log_parameter](#experimentlog_parameter).

        e.g:
        ```
        experiment = Experiment(api_key="MY_API_KEY")
        params = {
            "batch_size":64,
            "layer1":"LSTM(128)",
            "layer2":"LSTM(128)",
            "MAX_LEN":200
        }

        experiment.log_parameters(params)
        ```

        If you call this method multiple times with the same
        keys your values would be overwritten.  For example:

        ```
        experiment.log_parameters({"key1":"value1","key2":"value2"})
        ```
        On Comet.ml you will see the pairs of key1 and key2.

        If you then call:
        ```
        experiment.log_parameters({"key1":"other value"})l
        ```
        On the UI you will see the pairs key1: other value, key2: value2


        """
        self.set_step(step)

        if self.alive:
            for k in sorted(dic):
                if prefix is not None:
                    self.log_parameter(prefix + "_" + str(k), dic[k], self.curr_step)
                else:
                    self.log_parameter(k, dic[k], self.curr_step)

    def log_metrics(self, dic, prefix=None, step=None, epoch=None):
        """
        Logs a key,value dictionary of metrics.
        See also [`log_metric`](#experimentlog_metric)
        """
        self.set_step(step)
        self.set_epoch(epoch)

        if self.alive:
            for k in sorted(dic):
                if prefix is not None:
                    self.log_metric(
                        prefix + "_" + str(k), dic[k], self.curr_step, self.curr_epoch
                    )
                else:
                    self.log_metric(k, dic[k], self.curr_step, self.curr_epoch)

    def log_dataset_info(self, name=None, version=None, path=None):
        """
        Used to log information about your dataset.

        Args:
            name: Optional string representing the name of the dataset.
            version: Optional string representing a version identifier.
            path: Optional string that represents the path to the dataset.
                Potential values could be a file system path, S3 path
                or Database query.

        At least one argument should be included. The logged values will
        show on the `Other` tab.
        """
        if name is None and version is None and path is None:
            LOGGER.warning(
                "log_dataset_info: name, version, and path can't all be None"
            )
            return
        info = ""
        if name is not None:
            info += str(name)
        if version is not None:
            if info:
                info += "-"
            info += str(version)
        if path is not None:
            if info:
                info += ", "
            info += str(path)
        self.log_other("dataset_info", info)

    def log_dataset_hash(self, data):
        """
        Used to log the hash of the provided object. This is a best-effort hash computation which is based on the md5
        hash of the underlying string representation of the object data. Developers are encouraged to implement their
        own hash computation that's tailored to their underlying data source. That could be reported as
        `experiment.log_parameter("dataset_hash",your_hash).

        data: Any object that when casted to string (e.g str(data)) returns a value that represents the underlying data.

        """
        try:
            import hashlib

            data_hash = hashlib.md5(str(data).encode("utf-8")).hexdigest()
            self.log_parameter("dataset_hash", data_hash[:12])
        except Exception:
            LOGGER.warning(LOG_DATASET_ERROR, exc_info=True)

    def set_code(self, code, overwrite=False):
        """
        Sets the current experiment script's code. Should be called once per experiment.
        Args:
            code: String. Experiment source code.
            overwrite: Bool, if True, send the code
        """
        if self.alive and code is not None:

            if self._code_set and not overwrite:
                self._log_once_at_level(
                    logging.WARNING, "Set code ignored; already set and not overwrite"
                )
                return

            self._code_set = True

            message = self._create_message()
            message.set_code(code)
            self.streamer.put_messge_in_q(message)

    def set_model_graph(self, graph, overwrite=False):
        """
        Sets the current experiment computation graph.
        Args:
            graph: String or Google Tensorflow Graph Format.
            overwrite: Bool, if True, send the graph again
        """
        if self.alive:

            if self._graph_set and not overwrite:
                self._log_once_at_level(
                    logging.WARNING,
                    "Set model graph ignored; already set and not overwrite",
                )
                return

            self._graph_set = True

            LOGGER.debug("Set model graph called")

            if type(graph).__name__ == "Graph":  # Tensorflow Graph Definition
                from google.protobuf import json_format

                graph_def = graph.as_graph_def()
                graph = json_format.MessageToJson(graph_def)

            message = self._create_message()
            message.set_graph(graph)
            self.streamer.put_messge_in_q(message)

    def set_filename(self, fname):
        """
        Sets the current experiment filename.
        Args:
            fname: String. script's filename.
        """
        self.filename = fname
        if self.alive:
            message = self._create_message()
            message.set_filename(fname)
            self.streamer.put_messge_in_q(message)

    def set_name(self, name):
        """
        Set a name for the experiment. Useful for filtering and searching on Comet.ml.
        Will shown by default under the `Other` tab.
        Args:
            name: String. A name for the experiment.
        """
        self.log_other("Name", name)

    def set_os_packages(self):
        """
        Reads the installed os packages and reports them to server
        as a message.
        Returns: None

        """
        if self.alive:
            try:
                os_packages_list = read_unix_packages()
                if os_packages_list is not None:
                    if self.config["comet.override_feature.sdk_os_packages_http"]:
                        LOGGER.debug("Using the experimental OsPackagesMessage")
                        os_message = OsPackagesMessage(os_packages_list)

                        self.streamer.put_messge_in_q(os_message)
                    else:
                        message = self._create_message()  # type: Message
                        message.set_os_packages(os_packages_list)

                        self.streamer.put_messge_in_q(message)
            except Exception:
                LOGGER.warning(
                    "Failing to collect the installed os packages", exc_info=True
                )

    def set_pip_packages(self):
        """
        Reads the installed pip packages using pip's CLI and reports them to server as a message.
        Returns: None

        """
        if self.alive:
            try:
                import pkg_resources

                installed_packages = [d for d in pkg_resources.working_set]
                installed_packages_list = sorted(
                    ["%s==%s" % (i.key, i.version) for i in installed_packages]
                )
                message = self._create_message()
                message.set_installed_packages(installed_packages_list)
                self.streamer.put_messge_in_q(message)
            except Exception:
                LOGGER.warning(
                    "Failing to collect the installed pip packages", exc_info=True
                )

    def set_cmd_args(self):
        if self.alive:
            args = get_cmd_args_dict()
            LOGGER.debug("Command line arguments %r", args)
            if args is not None:
                for k, v in args.items():
                    self.log_parameter(k, v)

    # Context context-managers

    @contextmanager
    def train(self):
        """
        A context manager to mark the beginning and the end of the training
        phase. This allows you to provide a namespace for metrics/params.
        For example:

        ```
        experiment = Experiment(api_key="MY_API_KEY")
        with experiment.train():
            model.fit(x_train, y_train)
            accuracy = compute_accuracy(model.predict(x_train),y_train) # returns the train accuracy
            experiment.log_metric("accuracy",accuracy) # this will be logged as train accuracy based on the context.
        ```

        """
        # Save the old context and set the new one
        old_context = self.context
        self.context = "train"

        yield self

        # Restore the old one
        self.context = old_context

    @contextmanager
    def validate(self):
        """
        A context manager to mark the beginning and the end of the validating
        phase. This allows you to provide a namespace for metrics/params.
        For example:

        ```
        with experiment.validate():
            pred = model.predict(x_validation)
            val_acc = compute_accuracy(pred, y_validation)
            experiment.log_metric("accuracy", val_acc) # this will be logged as validation accuracy based on the context.
        ```


        """
        # Save the old context and set the new one
        old_context = self.context
        self.context = "validate"

        yield self

        # Restore the old one
        self.context = old_context

    @contextmanager
    def test(self):
        """
        A context manager to mark the beginning and the end of the testing phase. This allows you to provide a namespace for metrics/params.
        For example:

        ```
        with experiment.test():
            pred = model.predict(x_test)
            test_acc = compute_accuracy(pred, y_test)
            experiment.log_metric("accuracy", test_acc) # this will be logged as test accuracy based on the context.
        ```

        """
        # Save the old context and set the new one
        old_context = self.context
        self.context = "test"

        yield self

        # Restore the old one
        self.context = old_context

    def get_keras_callback(self):
        """
        This method is deprecated. See Experiment.get_callback("keras")
        """
        LOGGER.warn(
            "Experiment.get_keras_callback() is deprecated; use Experiment.get_callback('keras')"
        )
        return self.get_callback("keras")

    def disable_mp(self):
        """ Disabling the auto-collection of metrics and monkey-patching of
        the Machine Learning frameworks.
        """
        self.disabled_monkey_patching = True

    def register_callback(self, function):
        """
        Register the function passed as argument to be a RPC.
        Args:
            function: Callable.
        """
        function_name = function.__name__

        if isinstance(function, types.LambdaType) and function_name == "<lambda>":
            raise LambdaUnsupported()

        if function_name in self.rpc_callbacks:
            raise RPCFunctionAlreadyRegistered(function_name)

        self.rpc_callbacks[function_name] = function

    def unregister_callback(self, function):
        """
        Unregister the function passed as argument.
        Args:
            function: Callable.
        """
        function_name = function.__name__

        self.rpc_callbacks.pop(function_name, None)

    def _get_source_code(self):
        """Inspects the stack to detect calling script. Reads source code
        from disk and logs it.
        """
        if self._in_jupyter_environment():
            return None  # upload it with experiment.end()
        else:
            return get_caller_source_code()
        LOGGER.warning("Failed to find source code module")

    def _in_jupyter_environment(self):
        """
        Check to see if code is running in a Jupyter environment,
        including jupyter notebook, lab, or console.
        """
        try:
            import IPython
        except Exception:
            return False

        ipy = IPython.get_ipython()
        if ipy is None or not hasattr(ipy, "kernel"):
            return False
        else:
            return True

    def _in_ipython_environment(self):
        """
        Check to see if code is running in an IPython environment.
        """
        try:
            import IPython
        except Exception:
            return False

        ipy = IPython.get_ipython()
        if ipy is None:
            return False
        else:
            return True

    def _get_filename(self):
        """
        Get the filename of the executing code, if possible.
        """
        if self._in_jupyter_environment():
            return "Jupyter interactive"
        elif sys.argv:
            pathname = os.path.dirname(sys.argv[0])
            abs_path = os.path.abspath(pathname)
            filename = os.path.basename(sys.argv[0])
            full_path = os.path.join(abs_path, filename)
            return full_path

        return None

    def set_git_metadata(self):
        if not self.alive:
            return

        from .git_logging import (
            get_git_metadata,
        )  # Dulwich imports fails when running in sitecustomize.py

        current_path = os.getcwd()

        git_metadata = get_git_metadata(current_path)

        if git_metadata:
            message = self._create_message()
            message.set_git_metadata(git_metadata)
            self.streamer.put_messge_in_q(message)

    def _upload_git_patch(self):
        if not self.alive:
            return

        from .git_logging import (
            find_git_patch,
        )  # Dulwich imports fails when running in sitecustomize.py

        current_path = os.getcwd()
        git_patch = find_git_patch(current_path)
        if not git_patch:
            LOGGER.debug("Git patch is empty, nothing to upload")
            return

        archive, zip_path = compress_git_patch(git_patch)
        self._file_upload(zip_path, "git-patch", clean=True)
        LOGGER.debug("Git patch upload launched")

    def _log_env_details(self):
        if self.alive:
            message = self._create_message()
            message.set_env_details(get_env_details())
            self.streamer.put_messge_in_q(message)

    def _start_gpu_thread(self):
        if not self.alive:
            return

        # First sends the static info as a message
        gpu_static_info = get_gpu_static_info()
        message = self._create_message()
        message.set_gpu_static_info(gpu_static_info)
        self.streamer.put_messge_in_q(message)

        # Them sends the one-time metrics
        one_time_gpu_metrics = get_initial_gpu_metric()
        metrics = convert_gpu_details_to_metrics(one_time_gpu_metrics)
        for metric in metrics:
            self.log_metric(metric["name"], metric["value"])

        # Now starts the thread that will be called recurrently
        self.gpu_thread = GPULoggingThread(
            DEFAULT_GPU_MONITOR_INTERVAL, self._log_gpu_details
        )
        self.gpu_thread.start()

        # Connect streamer and the threads:
        self.streamer.on_gpu_monitor_interval = self.gpu_thread.update_interval

    def _start_cpu_thread(self):
        if not self.alive:
            return

        # Start the thread that will be called recurrently
        self.cpu_thread = CPULoggingThread(
            DEFAULT_CPU_MONITOR_INTERVAL, self._log_cpu_details
        )
        self.cpu_thread.start()

        # Connect the streamer and the cpu thread
        self.streamer.on_cpu_monitor_interval = self.cpu_thread.update_interval

    def _log_cpu_details(self, metrics):
        for metric in metrics:
            self.log_metric(metric, metrics[metric], include_context=False)

    def _log_gpu_details(self, gpu_details):
        metrics = convert_gpu_details_to_metrics(gpu_details)
        for metric in metrics:
            self.log_metric(metric["name"], metric["value"], include_context=False)

    def _file_upload(
        self, upload_file, upload_type, url_params=None, copy_to_tmp=False, clean=None
    ):
        # If we cannot remove the uploaded file or need the file content will
        # be frozen to the time the upload call is made, pass copy_to_tmp with
        # True value
        if copy_to_tmp is True:
            tmpfile = tempfile.NamedTemporaryFile(delete=False)
            shutil.copyfile(upload_file, tmpfile.name)
            upload_file = tmpfile.name
            if clean is None:
                # Clean the temporary file after upload
                clean = True
        else:
            if clean is None:
                # Don't risk cleaning an existing file
                clean = False

        upload_message = UploadFileMessage(
            upload_file, upload_type, url_params, clean=clean
        )
        self.streamer.put_messge_in_q(upload_message)

        return True  # The upload was successful

    def _get_uploaded_asset_url(self, asset_id):
        web_url = format_url(
            self.upload_web_asset_url_prefix, assetId=asset_id, experimentKey=self.id
        )
        api_url = format_url(
            self.upload_api_asset_url_prefix, assetId=asset_id, experimentKey=self.id
        )
        return {"web": web_url, "api": api_url}

    def _get_uploaded_image_url(self, image_id):
        web_url = format_url(
            self.upload_web_image_url_prefix, imageId=image_id, experimentKey=self.id
        )
        api_url = format_url(
            self.upload_api_image_url_prefix, imageId=image_id, experimentKey=self.id
        )
        return {"web": web_url, "api": api_url}

    def _get_uploaded_figure_url(self, figure_id):
        web_url = format_url(
            self.upload_web_image_url_prefix, imageId=figure_id, experimentKey=self.id
        )
        api_url = format_url(
            self.upload_api_image_url_prefix, imageId=figure_id, experimentKey=self.id
        )
        return {"web": web_url, "api": api_url}

    def _get_uploaded_audio_url(self, audio_id):
        web_url = format_url(
            self.upload_web_asset_url_prefix, assetId=audio_id, experimentKey=self.id
        )
        api_url = format_url(
            self.upload_api_asset_url_prefix, assetId=audio_id, experimentKey=self.id
        )
        return {"web": web_url, "api": api_url}

    def _add_pending_call(self, rpc_call):
        self._pending_calls.append(rpc_call)

    def _check_rpc_callbacks(self):
        while len(self._pending_calls) > 0:
            call = self._pending_calls.pop()
            if call is not None:
                try:
                    self._call_rpc_callback(call)
                except Exception:
                    LOGGER.debug("Failed to call rpc %r", call, exc_info=True)

    def _call_rpc_callback(self, rpc_call):
        if rpc_call.cometDefined is False:
            function_name = rpc_call.functionName

            start_time = local_timestamp()

            try:
                function = self.rpc_callbacks[function_name]
                remote_call_result = call_remote_function(function, self, rpc_call)
            except KeyError:
                error = "Unregistered remote action %r" % function_name
                remote_call_result = {"success": False, "error": error}

            end_time = local_timestamp()

            # Send the result to the backend
            self.connection.send_rpc_result(
                rpc_call.callId, remote_call_result, start_time, end_time
            )

            return

        # Hardcoded internal callbacks
        if rpc_call.functionName == "stop":
            self.log_other("experiment_stopped_by_user", True)
            raise InterruptedExperiment(rpc_call.userName)
        else:
            raise NotImplementedError()

    def add_tag(self, tag):
        """
        Add a tag to the experiment. Tags will be shown in the dashboard.
        Args:
            tag: String. A tag to add to the experiment.
        """
        try:
            self.tags.add(tag)
            return True
        except Exception:
            LOGGER.warning(ADD_TAGS_ERROR, tag, exc_info=True)
            return False

    def add_tags(self, tags):
        """
        Add several tags to the experiment. Tags will be shown in the
        dashboard.
        Args:
            tag: List<String>. Tags list to add to the experiment.
        """
        try:
            self.tags = self.tags.union(tags)
            return True
        except Exception:
            LOGGER.warning(ADD_TAGS_ERROR, tags, exc_info=True)
            return False

    def get_tags(self):
        """
        Return the tags of this experiment.
        Returns: set<String>. The set of tags.
        """
        return list(self.tags)

    def _set_optimizer(self, optimizer, pid, trial, count):
        """
        Set the optimizer dictionary and logs
        optimizer data.

        Arguments:
            optimizer: the Optimizer object
            pid: the parameter set id
            trial: the trial number
            count: the running count
        """
        self.optimizer = {
            "optimizer": optimizer,
            "pid": pid,
            "trial": trial,
            "count": count,
        }

    def set_predictor(self, predictor):
        """
        Set the predictor.
        """
        LOGGER.debug("Set experiment._predictor")
        self._predictor = predictor

    def get_predictor(self):
        """
        Get the predictor.
        """
        return self._predictor

    def stop_early(self, epoch):
        """
        Should the experiment stop early?
        """
        if self._predictor:
            return self._predictor.stop_early(epoch=epoch)
        else:
            return False

    def get_callback(self, framework, *args, **kwargs):
        """
        Get a callback for a particular framework.

        When framework == 'keras' then return an instance of
        Comet.ml's Keras callback.

        When framework == 'tf-keras' then return an instance of
        Comet.ml's TensorflowKeras callback.

        Note:
            The keras callbacks are added to your Keras `model.fit()`
            callbacks list automatically to report model training metrics
            to Comet.ml so you do not need to add them manually.
        """
        if framework in ["keras", "tf-keras"]:
            if framework == "keras":
                from .callbacks._keras import KerasCallback, EmptyKerasCallback
            elif framework == "tf-keras":
                from .callbacks._tensorflow_keras import (
                    KerasCallback,
                    EmptyKerasCallback,
                )

            if self.alive:
                return KerasCallback(
                    self,
                    log_params=self.auto_param_logging,
                    log_metrics=self.auto_metric_logging,
                    log_graph=self.log_graph,
                )
            else:
                return EmptyKerasCallback()
        else:
            raise NotImplementedError(
                "No such framework for callback: `%s`" % framework
            )

    def get_predictor_callback(self, framework, *args, **kwargs):
        """
        Get a predictor callback for a particular framework.

        Possible frameworks are:

        * "keras" - return a callback for keras predictive early stopping
        * "tf-keras" - return a callback for tensorflow.keras predictive early stopping
        * "tensorflow" - return a callback for tensorflow predictive early stopping
        """
        if framework == "keras":
            from .callbacks._keras import PredictiveEarlyStoppingKerasCallback

            predictor = self.get_predictor()
            if predictor is not None:
                return PredictiveEarlyStoppingKerasCallback(predictor, *args, **kwargs)
            else:
                raise Exception("No predictor is set")

        elif framework == "tf-keras":
            from .callbacks._tensorflow_keras import (
                PredictiveEarlyStoppingKerasCallback,
            )

            predictor = self.get_predictor()
            if predictor is not None:
                return PredictiveEarlyStoppingKerasCallback(predictor, *args, **kwargs)
            else:
                raise Exception("No predictor is set")

        elif framework == "tensorflow":
            from .callbacks._tensorflow import TensorflowPredictorStopHook

            predictor = self.get_predictor()
            if predictor is not None:
                return TensorflowPredictorStopHook(predictor, *args, **kwargs)
            else:
                raise Exception("No predictor is set")

        else:
            raise NotImplementedError(
                "No such framework for predictor callback: `%s`" % framework
            )

    def send_notification(self, title, status=None, additional_data=None):
        """
        Send yourself a notification through email when an experiment
        ends.

        Args:
            title: str - the email subject.
            status: str - the final status of the experiment. Typically,
                something like "finished", "completed" or "aborted".
            additional_data: dict - a dictionary of key/values to notify.

        Note:
            In order to receive the notification, you need to have turned
            on Notifications in your Settings in the Comet user interface.

        If you wish to have the `additional_data` saved with the
        experiment, you should also call `Experiment.log_other()` with
        this data as well.

        This method uses the email address associated with your account.
        """
        pass
