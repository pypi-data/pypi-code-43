# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import os
import sys

from azureml.telemetry import get_telemetry_log_handler
from azureml.core.run import Run, _SubmittedRun


"""Telemetry utils."""

OPENDATASETS_LOGGER_NAMESPACE = "azureml.opendatasets"
OPENDATASETS_INSTRUMENTATION_KEY = 'f65df220-4460-4269-b954-a11c54f8e611'
OPENDATASETS_METRICS_LABEL_ENV_VAR = 'AZUREML_OPENDATASETS_METRICS_LABEL'


def add_appinsights_log_handler(logger):
    handler = get_telemetry_log_handler(
        instrumentation_key=OPENDATASETS_INSTRUMENTATION_KEY,
        component_name=OPENDATASETS_LOGGER_NAMESPACE)
    add_handler(logger, handler)


def add_console_log_handler(logger):
    handler = logging.StreamHandler(sys.stdout)
    add_handler(logger, handler)


def get_opendatasets_logger(name, verbosity=logging.DEBUG):
    logger = logging.getLogger(OPENDATASETS_LOGGER_NAMESPACE).getChild(name)
    logger.propagate = False
    logger.setLevel(verbosity)
    add_appinsights_log_handler(logger)
    add_console_log_handler(logger)
    return logger


def add_handler(logger, handler):
    """
    Add a logger handler and skip if the same type already exists.

    :param logger: Logger
    :param handler: handler instance
    """
    handler_type = type(handler)
    for log_handler in logger.handlers:
        if isinstance(log_handler, handler_type):
            return
    logger.addHandler(handler)


def get_run_common_properties():
    run = Run.get_context()
    metrics_label = get_opendatasets_metrics_label()
    if isinstance(run, _SubmittedRun):
        context = run._experiment.workspace.service_context
        subscription_id = context.subscription_id
        resource_group_name = context.resource_group_name
        workspace_name = context.workspace_name
        experiment_name = run._experiment.name
        run_id = run._run_id
        return {
            'IsSubmittedRun': True,
            'SubscriptionId': subscription_id,
            'ResourceGroupName': resource_group_name,
            'WorkspaceName': workspace_name,
            'ExperimentName': experiment_name,
            'RunId': run_id,
            'MetricsLabel': metrics_label
        }
    else:
        return {
            'IsSubmittedRun': False,
            'MetricsLabel': metrics_label
        }


def get_opendatasets_metrics_label():
    value = os.environ.get(OPENDATASETS_METRICS_LABEL_ENV_VAR)
    return value
