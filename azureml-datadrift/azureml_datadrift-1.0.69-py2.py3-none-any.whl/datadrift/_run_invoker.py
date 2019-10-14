# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import argparse

from azureml.datadrift._restclient import DataDriftClient
from azureml.datadrift._logging._telemetry_logger import _TelemetryLogger
from azureml.datadrift._logging._telemetry_logger_context_filter import _TelemetryLoggerContextFilter
from azureml.core.run import Run
from azureml.datadrift._utils.constants import DATADRIFT_RUN_INVOKER

module_logger = _TelemetryLogger.get_telemetry_logger('_run_invoker')


def submit(datadrift_id, logger):
    run = Run.get_context(allow_offline=False)
    ws = run.experiment.workspace

    logger.info("Workspace: {}, SubscriptionId: {}, ResourceGroup: {}, RunId: {}".format(
        ws.name,
        ws.subscription_id,
        ws.resource_group,
        run.id
    ))

    logger.info("Sending a new schedule run to DataDrift service")
    _TelemetryLogger.log_event(DATADRIFT_RUN_INVOKER, **{
        'workspace_id': ws._workspace_id, 'workspace_name': ws.name,
        'workspace_location': ws.location, 'subscription_id': ws.subscription_id
    })
    dd_client = DataDriftClient(ws.service_context)
    res = dd_client.schedule_run(datadrift_id)
    logger.info("ExecutionRunId: {}".format(res.execution_run_id))

    return res


def main():
    parser = argparse.ArgumentParser("script")
    parser.add_argument("--datadrift_id", type=str, help="DataDrift Id")
    args = parser.parse_args()

    module_logger.addFilter(_TelemetryLoggerContextFilter({'datadrift_id': args.datadrift_id}))

    with _TelemetryLogger.log_activity(module_logger, activity_name="_run_invoker") as logger:
        logger.info("Submitting a new run...")
        submit(args.datadrift_id, logger)
        logger.info("The run has been submitted.")


if __name__ == '__main__':
    main()
