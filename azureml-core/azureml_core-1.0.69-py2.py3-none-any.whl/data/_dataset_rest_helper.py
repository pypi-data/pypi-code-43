# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains helper methods for dataset service REST APIs."""

import os
from copy import deepcopy

from msrest.authentication import BasicTokenAuthentication
from msrest.exceptions import HttpOperationError
from azureml.data.constants import _DATASET_TYPE_TABULAR, _DATASET_TYPE_FILE
from azureml.data._loggerfactory import _LoggerFactory
from azureml._base_sdk_common import _ClientSessionId
from azureml._base_sdk_common.service_discovery import get_service_url
from azureml._restclient.models.dataset_state_dto import DatasetStateDto
from azureml._restclient.models.dataset_definition_dto import DatasetDefinitionDto
from azureml._restclient.models.dataset_dto import DatasetDto
from azureml._restclient.models.saved_dataset_dto import SavedDatasetDto
from azureml._restclient.rest_client import RestClient


_logger = None


def _get_logger():
    global _logger
    if _logger is not None:
        return _logger
    _logger = _LoggerFactory.get_logger(__name__)
    return _logger


def _dataset_to_dto(dataset, name, description=None, tags=None):
    from azureml.data._dataset_client import _DatasetClient

    # keep old Dataset client which relies on file_type working
    file_type = _DatasetClient._get_source_file_type(dataset._dataflow)
    dataset_type = _get_type(dataset)

    dataset_definition_dto = DatasetDefinitionDto(
        dataflow=dataset._dataflow.to_json(),
        properties=deepcopy(dataset._properties),
        dataset_definition_state=DatasetStateDto(),
        file_type=file_type)

    return DatasetDto(
        name=name,
        dataset_type=dataset_type,
        latest=dataset_definition_dto,
        description=description,
        tags=tags,
        is_visible=True)


def _dto_to_dataset(workspace, dto):
    if not isinstance(dto, DatasetDto):
        raise RuntimeError('dto has to be instance of DatasetDto')

    from azureml.data.tabular_dataset import TabularDataset
    from azureml.data.file_dataset import FileDataset
    from azureml.data.dataset_factory import FileDatasetFactory
    from azureml.data._dataset import _DatasetRegistration

    version = _resolve_dataset_version(dto.latest.version_id)
    registration = _DatasetRegistration(
        workspace=workspace, saved_id=dto.latest.saved_dataset_id, registered_id=dto.dataset_id,
        name=dto.name, version=version, description=dto.description, tags=dto.tags)

    dataflow_json = dto.latest.dataflow
    if dataflow_json is None or len(dataflow_json) == 0:
        # migrate legacy dataset which has empty dataflow to FileDataset
        data_path = dto.latest.data_path
        if not data_path or 'datastore_name' not in data_path or 'relative_path' not in data_path:
            error = 'Dataset should not have empty dataflow. workspace={}, saved_id={}'.format(
                workspace, registration.saved_id)
            _get_logger().error(error)
            raise error

        from azureml.core import Datastore
        store = Datastore.get(workspace, data_path.datastore_name)
        dataset = FileDatasetFactory.from_files((store, data_path.relative_path))
        dataset._registration = registration
        return dataset

    ds_type = _resolve_dataset_type(dto.dataset_type)
    if ds_type == _DATASET_TYPE_TABULAR:
        return TabularDataset._create(
            definition=dataflow_json,
            properties=dto.latest.properties,
            registration=registration)
    if dto.dataset_type == _DATASET_TYPE_FILE:
        return FileDataset._create(
            definition=dataflow_json,
            properties=dto.latest.properties,
            registration=registration)


def _dataset_to_saved_dataset_dto(dataset):
    dataset_type = _get_type(dataset)
    return SavedDatasetDto(
        dataset_type=dataset_type,
        properties=deepcopy(dataset._properties),
        dataflow_json=dataset._dataflow.to_json())


def _saved_dataset_dto_to_dataset(workspace, dto):
    from azureml.data._dataset import _DatasetRegistration
    from azureml.data.tabular_dataset import TabularDataset
    from azureml.data.file_dataset import FileDataset

    registration = _DatasetRegistration(workspace=workspace, saved_id=dto.id)
    dataflow_json = dto.dataflow_json

    if dto.dataset_type == _DATASET_TYPE_FILE:
        return FileDataset._create(
            definition=dataflow_json,
            properties=dto.properties,
            registration=registration)
    if dto.dataset_type == _DATASET_TYPE_TABULAR:
        return TabularDataset._create(
            definition=dataflow_json,
            properties=dto.properties,
            registration=registration)
    raise RuntimeError('Unrecognized dataset type "{}"'.format(dto.dataset_type))


def _resolve_dataset_version(version):
    try:
        return int(version)
    except ValueError:
        _get_logger().warning('Unrecognized dataset version "{}".'.format(version))
        return None


def _resolve_dataset_type(ds_type):
    if ds_type in [_DATASET_TYPE_TABULAR, _DATASET_TYPE_FILE]:
        return ds_type
    if ds_type is not None:
        _get_logger().warning('Unrecognized dataset type "{}".'.format(ds_type))
    # migrate legacy dataset which has dataflow to TabularDataset
    return _DATASET_TYPE_TABULAR


def _get_workspace_uri_path(subscription_id, resource_group, workspace_name):
    return ('/subscriptions/{}/resourceGroups/{}/providers'
            '/Microsoft.MachineLearningServices'
            '/workspaces/{}').format(subscription_id, resource_group, workspace_name)


def _get_type(dataset):
    from azureml.data.tabular_dataset import TabularDataset
    from azureml.data.file_dataset import FileDataset

    if isinstance(dataset, TabularDataset):
        return _DATASET_TYPE_TABULAR
    elif isinstance(dataset, FileDataset):
        return _DATASET_TYPE_FILE
    else:
        raise RuntimeError('Unrecognized dataset type "{}"'.format(type(dataset)))


def _make_request(request_fn, handle_error_fn=None):
    try:
        return (True, request_fn())
    except HttpOperationError as error:
        try:
            status_code = error.response.status_code
            if status_code >= 500 or status_code < 400:
                _get_logger().error('Request failed with {}: {}'.format(status_code, error.message))
            elif handle_error_fn:
                error = handle_error_fn(error) or error  # request specific error handling
        except Exception as exp:
            _get_logger().error('Exception while handling request error: {}'.format(exp))
        return (False, error)
    except Exception as other_exception:
        _get_logger().error('Request failed with: {}'.format(other_exception))
        return (False, other_exception)


def _restclient(ws):
    host_env = os.environ.get('AZUREML_SERVICE_ENDPOINT')
    auth = ws._auth
    host = host_env or get_service_url(
        auth,
        _get_workspace_uri_path(
            ws._subscription_id,
            ws._resource_group,
            ws._workspace_name),
        ws._workspace_id)

    auth_header = ws._auth.get_authentication_header()['Authorization']
    access_token = auth_header[7:]  # 7 == len('Bearer ')

    return RestClient(base_url=host, credentials=BasicTokenAuthentication({
        'access_token': access_token
    }))


_custom_headers = {'x-ms-client-session-id': _ClientSessionId}
