# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Run script for dataset profile run."""

import sys
from azureml.core import Run
from azureml.data._dataset_client import _DatasetClient
from azureml._restclient.artifacts_client import ArtifactsClient

if __name__ == '__main__':
    dataset_id = sys.argv[1]
    action_id = sys.argv[2]
    dataflow_artifact_id = sys.argv[3]
    print('Start running action, id = {}, for dataset, id = {}'.format(action_id, dataset_id))
    workspace = Run.get_context().experiment.workspace
    dataflow_json = None
    if dataflow_artifact_id:
        artifacts_client = ArtifactsClient(workspace.service_context)
        [origin, container, path] = dataflow_artifact_id.split('/', 2)
        dataflow_json = artifacts_client.download_artifact_contents_to_string(origin, container, path)
    _DatasetClient._execute_dataset_action(workspace, dataset_id, action_id, dataflow_json)
