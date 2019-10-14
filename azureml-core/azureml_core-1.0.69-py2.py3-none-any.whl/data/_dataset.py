# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Abstract Dataset class."""

import collections
import re
import json
from abc import ABCMeta
from copy import deepcopy

from azureml.data.dataset_factory import TabularDatasetFactory, FileDatasetFactory, _LabeledDatasetFactory
from azureml.data.constants import _DATASET_TYPE_TABULAR, _TELEMETRY_ENTRY_POINT_DATASET
from azureml.data._dataprep_helper import dataprep
from azureml.data._dataset_rest_helper import _dto_to_dataset, _dataset_to_dto, _dataset_to_saved_dataset_dto, \
    _saved_dataset_dto_to_dataset, _restclient, _resolve_dataset_type, _custom_headers, _make_request
from azureml.data._loggerfactory import track, _LoggerFactory
from azureml.data.dataset_consumption_config import DatasetConsumptionConfig


_PUBLIC_API = 'PublicApi'
_logger = None


def _get_logger():
    global _logger
    if _logger is None:
        _logger = _LoggerFactory.get_logger(__name__)
    return _logger


class _Dataset(object):
    """Base class of datasets in Azure Machine Learning service."""

    __metaclass__ = ABCMeta

    Tabular = TabularDatasetFactory
    File = FileDatasetFactory
    _Labeled = _LabeledDatasetFactory

    def __init__(self):
        """Class _Dataset constructor.

        This constructor is not supposed to be invoked directly. Dataset is intended to be created using
        :class:`azureml.data.dataset_factory.TabularDatasetFactory` class and
        :class:`azureml.data.dataset_factory.FileDatasetFactory` class.
        """
        if self.__class__ == _Dataset:
            raise RuntimeError('Cannot create instance of absctract class _Dataset')
        self._definition = None
        self._properties = None
        self._registration = None
        self._telemetry_info = None

    @staticmethod
    @track(_get_logger, activity_type=_PUBLIC_API)
    def get_by_name(workspace, name, version='latest'):
        """Get a registered Dataset from workspace by its registration name.

        :param workspace: The existing AzureML workspace in which the Dataset was registered.
        :type workspace: azureml.core.Workspace
        :param name: The registration name.
        :type name: str
        :param version: The registration version. Defaults to 'latest'.
        :type version: int
        :return: The registered dataset object.
        :rtype: azureml.data.TabularDataset or azureml.data.FileDataset
        """
        is_latest = version == 'latest'
        if not is_latest:
            try:
                version = int(version)
            except ValueError:
                raise ValueError('Invalid value {} for version. Version value must be number or "latest".'
                                 .format(version))

        def request():
            dto = _restclient(workspace).dataset.get_dataset_by_name(
                workspace.subscription_id,
                workspace.resource_group,
                workspace.name,
                dataset_name=name,
                include_latest_definition=is_latest,
                custom_headers=_custom_headers)
            if not is_latest:
                definition_dto = _restclient(workspace).dataset.get_dataset_definition(
                    workspace.subscription_id,
                    workspace.resource_group,
                    workspace.name,
                    dataset_id=dto.dataset_id,
                    version=str(version),
                    custom_headers=_custom_headers)
                dto.latest = definition_dto
            return dto

        def handle_error(error):
            if error.response.status_code == 404:
                return Exception(
                    'Cannot find dataset registered with name "{}"{} in the workspace.'
                    .format(name, '' if version == 'latest' else ' (version: {})'.format(version)))

        success, result = _make_request(request, handle_error)
        if not success:
            raise result
        return _dto_to_dataset(workspace, result)

    @staticmethod
    @track(_get_logger, activity_type=_PUBLIC_API)
    def get_by_id(workspace, id):
        """Get a Dataset which is saved to the workspace.

        :param workspace: The existing AzureML workspace in which the Dataset is saved.
        :type workspace: azureml.core.Workspace
        :param id: The id of dataset.
        :type id: str
        :return: The registered dataset object.
        :rtype: azureml.data.TabularDataset or azureml.data.FileDataset
        """
        def request():
            return _restclient(workspace).dataset.get_by_id(
                subscription_id=workspace.subscription_id,
                resource_group_name=workspace.resource_group,
                workspace_name=workspace.name,
                id=id,
                custom_headers=_custom_headers)

        def handle_error(error):
            if error.response.status_code == 404:
                return Exception(
                    'Cannot find dataset with id "{}" in the workspace.'
                    .format(id))

        success, result = _make_request(request, handle_error)
        if not success:
            raise result
        return _saved_dataset_dto_to_dataset(workspace, result)

    @staticmethod
    @track(_get_logger, activity_type=_PUBLIC_API)
    def get_all(workspace):
        """Get all the registered datasets in the workspace.

        :param workspace: The existing AzureML workspace in which the Datasets were registered.
        :type workspace: azureml.core.Workspace
        :return: A dictionary of TabularDataset and FileDataset objects keyed by their registration name.
        :rtype: dict[str, azureml.data.TabularDataset or azureml.data.FileDataset]
        """
        def list_dataset(continuation_token):
            return _restclient(workspace).dataset.list(
                subscription_id=workspace.subscription_id,
                resource_group_name=workspace.resource_group,
                workspace_name=workspace.name,
                page_size=100,
                include_latest_definition=False,
                include_invisible=False,
                continuation_token=continuation_token,
                custom_headers=_custom_headers)

        def get_dataset(name):
            try:
                return _Dataset.get_by_name(workspace, name)
            except Exception:
                return None

        return _DatasetDict(list_fn=list_dataset, get_fn=get_dataset)

    @property
    @track(_get_logger, activity_type=_PUBLIC_API)
    def id(self):
        """Return the identifier of the dataset.

        :return: Dataset id. If the dataset is not saved to any workspace, the id will be None.
        :rtype: str
        """
        if self._registration:
            if self._registration.saved_id:
                return self._registration.saved_id
            if self._registration.workspace:
                self._ensure_saved(self._registration.workspace)
                return self._registration.saved_id
        return None

    @property
    @track(_get_logger, activity_type=_PUBLIC_API)
    def name(self):
        """Return the registration name.

        :return: Dataset name.
        :rtype: str
        """
        return None if self._registration is None else self._registration.name

    @property
    @track(_get_logger, activity_type=_PUBLIC_API)
    def version(self):
        """Return the registration version.

        :return: Dataset version.
        :rtype: int
        """
        return None if self._registration is None else self._registration.version

    @property
    @track(_get_logger, activity_type=_PUBLIC_API)
    def description(self):
        """Return the registration description.

        :return: Dataset description.
        :rtype: str
        """
        return None if self._registration is None else self._registration.description

    @property
    @track(_get_logger, activity_type=_PUBLIC_API)
    def tags(self):
        """Return the registration tags.

        :return: Dataset tags.
        :rtype: str
        """
        return None if self._registration is None else self._registration.tags

    @property
    @track(_get_logger, activity_type=_PUBLIC_API)
    def data_changed_time(self):
        """Return the source data changed time.

        .. remarks::

            Data changed time is available for file-based data source. None will be returned when the data source is
            not supported for checking when change has happened.

        :return: The time when the most recent change happened to source data.
        :rtype: datetime.datetime
        """
        _, changed_time = self._dataflow._get_source_data_hash()
        return changed_time

    @property
    @track(_get_logger)
    def _dataflow(self):
        if self._definition is None:
            raise RuntimeError('Dataset definition is missing. Please check how the dataset is created.')
        if not isinstance(self._definition, dataprep().Dataflow):
            self._definition = dataprep().Dataflow.from_json(self._definition)
        return self._definition

    @track(_get_logger, activity_type=_PUBLIC_API)
    def as_named_input(self, name):
        """Provide a name for this dataset which will be used to retrieve the materialized dataset in the run.

        .. remarks::

            The name here will only be applicable inside an Azure Machine Learning run. You can use this name to
            retrieve the dataset in the context of a run using two approaches:

            #. Environment Variable:
                The name will be the environment variable name and the materialized dataset will
                be made available as the value of the environment variable. If the dataset is downloaded or mounted,
                the value will be the downloaded/mounted path. For example:

                .. code-block:: python

                    # in your job submission notebook/script:
                    dataset.as_named_input('foo').as_download('/tmp/dataset')

                    # in the script that will be executed in the run
                    import os
                    path = os.environ['foo'] # path will be /tmp/dataset

                If the dataset is set to direct mode, then the value will be the dataset ID. You can then
                retrieve the dataset object by doing `Dataset.get_by_id(os.environ['foo'])`

            #. Run.input_datasets:
                This is a dictionary where the key will be the dataset name you specified in this
                method and the value will be the materialized dataset. For downloaded and mounted dataset, the value
                will be the downloaded/mounted path. For direct mode, the value will be the same dataset object you
                specified in your job submission script.

                .. code-block:: python

                    # in your job submission notebook/script:
                    dataset.as_named_input('foo') # direct mode

                    # in the script that will be executed in the run
                    run = Run.get_context()
                    run.input_datasets['foo'] # this returns the dataset object from above.

        :param name: The name of the dataset for the run.
        :type name: str
        :return: The configuration object describing how the Dataset should be materialized in the run.
        :rtype: azureml.data.dataset_consumption_config.DatasetConsumptionConfig
        """
        return DatasetConsumptionConfig(name, self)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def register(self, workspace, name, description=None, tags=None, create_new_version=False):
        """Register the dataset to the provided workspace.

        :param workspace: The workspace to register the dataset.
        :type workspace: azureml.core.Workspace
        :param name: The name to register the dataset with.
        :type name: str
        :param description: A text description of the dataset. Defaults to None.
        :type description: str
        :param tags: Dictionary of key value tags to give the dataset. Defaults to None.
        :type tags: dict[str, str]
        :param create_new_version: Boolean to register the dataset as a new version under the specified name.
        :type create_new_version: bool
        :return: The registered dataset object.
        :rtype: azureml.data.TabularDataset or azureml.data.FileDataset
        """
        def request():
            return _restclient(workspace).dataset.register(
                workspace.subscription_id,
                workspace.resource_group,
                workspace.name,
                dataset_dto=_dataset_to_dto(self, name, description, tags),
                if_exists_ok=create_new_version,
                update_definition_if_exists=create_new_version,
                custom_headers=self._get_telemetry_headers())

        def handle_error(error):
            status_code = error.response.status_code
            if status_code == 409:
                return Exception((
                    'There is already a dataset registered under name "{}". ' +
                    'Specify `create_new_version=True` to register the dataset as a new version.'
                ).format(name))
            if status_code == 400:
                regex = re.compile(
                    r"has been used in version '([0-9]+)' of an existing registered dataset named '(.+)'.",
                    re.IGNORECASE)
                matches = regex.findall(error.message)
                if len(matches) == 1:
                    existing_version, existing_name = matches[0]
                    return Exception((
                        'An identical dataset had already been registered, which can ' +
                        'be retrieved with `Dataset.get_by_name(workspace, name="{}", version={})`.'
                    ).format(existing_name, existing_version))

        success, result = _make_request(request, handle_error)
        if not success:
            raise result
        return _dto_to_dataset(workspace, result)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def unregister_all_versions(self):
        """Unregister all versions under the registration name of this dataset from the workspace.

        .. remarks::

            The operation does not change any source data.
        """
        if not self._registration or not self._registration.workspace or not self._registration.registered_id:
            return  # no-op if dataset is not registered
        workspace = self._registration.workspace

        def request():
            return _restclient(workspace).dataset.unregister_dataset(
                workspace.subscription_id,
                workspace.resource_group,
                workspace.name,
                self.name,
                custom_headers=_custom_headers)

        success, result = _make_request(request)
        if not success:
            raise result
        self._registration = None

    @classmethod
    @track(_get_logger)
    def _create(cls, definition, properties=None, registration=None, telemetry_info=None):
        if registration is not None and not isinstance(registration, _DatasetRegistration):
            raise TypeError('registration must be instance of `_DatasetRegistration`')
        if telemetry_info is not None and not isinstance(telemetry_info, _DatasetTelemetryInfo):
            raise TypeError('telemetry_info must be instance of `_DatasetTelemetryInfo`')
        dataset = cls()
        dataset._definition = definition  # definition is either str or Dataflow which is immutable
        dataset._properties = deepcopy(properties) if properties else {}
        dataset._registration = registration
        dataset._telemetry_info = telemetry_info
        return dataset

    @track(_get_logger)
    def _ensure_saved(self, workspace):
        if not self._registration or not self._registration.saved_id:
            # only call service when dataset is not saved yet
            def request():
                return _restclient(workspace).dataset.ensure_saved(
                    subscription_id=workspace.subscription_id,
                    resource_group_name=workspace.resource_group,
                    workspace_name=workspace.name,
                    dataset=_dataset_to_saved_dataset_dto(self),
                    custom_headers=self._get_telemetry_headers())

            success, result = _make_request(request)
            if not success:
                raise result
            saved_dataset = _saved_dataset_dto_to_dataset(workspace, result)

            # modify _definition using service response
            self._definition = saved_dataset._definition

            # modify self._registration.saved_id using service response
            if self._registration:
                self._registration.saved_id = saved_dataset._registration.saved_id
            else:
                self._registration = saved_dataset._registration

        return self._registration.saved_id

    def _get_telemetry_headers(self):
        telemetry_entry_point = _TELEMETRY_ENTRY_POINT_DATASET
        if self._telemetry_info and self._telemetry_info.entry_point:
            telemetry_entry_point = self._telemetry_info.entry_point
        headers = {'x-ms-azureml-dataset-entry-point': telemetry_entry_point}
        headers.update(_custom_headers)
        return headers

    @track(_get_logger, activity_type=_PUBLIC_API)
    def __str__(self):
        """Format the dataset object into a string.

        :return: Return string representation of the dataset object
        :rtype: str
        """
        return '{}\n{}'.format(type(self).__name__, self.__repr__())

    @track(_get_logger, activity_type=_PUBLIC_API)
    def __repr__(self):
        """Format the dataset object into a string.

        :return: Return string representation of the the dataset object
        :rtype: str
        """
        try:
            # azureml-dataprep may not be installed, but print should not throw
            steps = self._dataflow._get_steps()
            step_type_pattern = re.compile(r'Microsoft.DPrep.(.*)Block', re.IGNORECASE)
            step_type = steps[0].step_type
            step_arguments = steps[0].arguments

            if hasattr(step_arguments, 'to_pod'):
                step_arguments = step_arguments.to_pod()
            if step_type == 'Microsoft.DPrep.GetDatastoreFilesBlock':
                source = [
                    '(\'{}\', \'{}\')'.format(store['datastoreName'], store['path'])
                    for store in step_arguments['datastores']
                ]
            elif step_type == 'Microsoft.DPrep.GetFilesBlock':
                source = [details['path'] for details in step_arguments['path']['resourceDetails']]
            else:
                source = None

            encoder = dataprep().api.engineapi.typedefinitions.CustomEncoder \
                if hasattr(dataprep().api.engineapi.typedefinitions, 'CustomEncoder') \
                else dataprep().api.engineapi.engine.CustomEncoder
            content = {
                'source': source,
                'definition': [
                    step_type_pattern.search(s.step_type).group(1) for s in steps
                ]
            }
        except ImportError:
            encoder = None
            content = {}

        if self._registration is not None:
            content['registration'] = {
                'name': self.name,
                'version': self.version
            }
            if self.description:
                content['registration']['description'] = self.description
            if self.tags:
                content['registration']['tags'] = self.tags
            content['registration']['workspace'] = self._registration.workspace.__repr__()

        return json.dumps(content, indent=2, cls=encoder)


class _DatasetRegistration(object):
    def __init__(self, workspace, saved_id, registered_id=None, name=None, version=None, description=None, tags=None):
        self.workspace = workspace
        self.saved_id = saved_id
        self.registered_id = registered_id
        self.name = name
        self.version = version
        self.description = description
        self.tags = tags


class _DatasetTelemetryInfo(object):
    def __init__(self, entry_point):
        self.entry_point = entry_point


_Mapping = collections.abc.Mapping if hasattr(collections, 'abc') else collections.Mapping


class _DatasetDict(_Mapping):
    def __init__(self, list_fn, get_fn):
        self._list_fn = list_fn
        self._get_fn = get_fn
        self._all_listed = False
        self._list_continuation_token = None
        self._list_cached = {}
        self._getitem_cached = {}

    def __getitem__(self, key):
        if key in self._getitem_cached:
            return self._getitem_cached[key]
        result = self._get_fn(name=key)
        if result is None:
            raise KeyError(key)
        self._getitem_cached[key] = result
        return result

    def __iter__(self):
        return iter(self._list_cached if self._all_listed else _DatasetDictKeyIterator(self))

    def __len__(self):
        while not self._all_listed:
            self._list_more()
        return len(self._list_cached)

    def __str__(self):
        while not self._all_listed:
            self._list_more()
        names = self._list_cached.keys()
        if not names:
            return '{}'
        longest = max(len(name) for name in names)
        content = '{'
        for name, registration in self._list_cached.items():
            ds_type, desc, tags = registration
            content += '\'{}\':{}{}('.format(
                name,
                ' ' * (1 + longest - len(name)),
                'TabularDataset' if ds_type == _DATASET_TYPE_TABULAR else 'FileDataset')
            if desc:
                content += 'description={}'.format(desc.__repr__())
                if tags:
                    content += ', '
            if tags:
                content += 'tags={}'.format(tags)
            content += '),\n '
        content = content[:-3] + '}'
        return content

    def __repr__(self):
        return self.__str__()

    def _list_more(self):
        new_listed_names = []
        if not self._all_listed:
            list_result = self._list_fn(continuation_token=self._list_continuation_token)
            if list_result.continuation_token is None:
                self._all_listed = True
            else:
                self._list_continuation_token = list_result.continuation_token
            for ds in list_result.value:
                if ds is not None:
                    self._list_cached[ds.name] = (_resolve_dataset_type(ds.dataset_type), ds.description, ds.tags)
                    new_listed_names.append(ds.name)
        return new_listed_names


class _DatasetDictKeyIterator():
    def __init__(self, ds_dict):
        self._ds_dict = ds_dict
        self._pending_keys = list(ds_dict._list_cached.keys())

    def __iter__(self):
        return self

    def __next__(self):
        if self._ds_dict._all_listed and not self._pending_keys == 0:
            raise StopIteration
        if not self._pending_keys:
            self._pending_keys.extend(self._ds_dict._list_more())
        if not self._pending_keys:
            raise StopIteration
        return self._pending_keys.pop(0)


def _get_path_from_step(step_type, step_arguments):
    if step_type == 'Microsoft.DPrep.GetDatastoreFilesBlock':
        datastores = step_arguments['datastores']
        if len(datastores) > 1:
            return None
        datastore = datastores[0]
        return '{}/{}'.format(datastore['datastoreName'], datastore['path'])
    if step_type == 'Microsoft.DPrep.GetFilesBlock':
        resource_details = step_arguments['path']['resourceDetails']
        if len(resource_details) > 1:
            return None
        return resource_details[0]['path']
    if step_type == 'Microsoft.DPrep.ReferenceAndInverseSplitBlock':
        source_step = step_arguments['sourceFilter']['anonymousSteps'][0]
        return _get_path_from_step(source_step['type'], source_step['arguments'])
    _get_logger().warning('Unrecognized type "{}" for first step in FileDataset.'.format(step_type))
    return None
