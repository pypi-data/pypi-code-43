# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains functionality to manage data context of datastores and datasets. Internal use only."""
import logging
import os
import re
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from azureml.core.datastore import Datastore
from azureml.core.runconfig import DataReferenceConfiguration, Data, DataLocation, Dataset
from azureml.data._dataset import _Dataset, _get_path_from_step
from azureml.data._dataprep_helper import dataprep
from azureml.data.file_dataset import FileDataset
from azureml.exceptions import UserErrorException, RunEnvironmentException
from six import raise_from

module_logger = logging.getLogger(__name__)
http_pattern = re.compile(r'^https?://', re.IGNORECASE)


def _log_and_print(msg):
    module_logger.debug(msg)
    print(msg)


class _CommonContextManager(object):
    """Context manager common part."""

    def __init__(self, config):
        """Class _CommonContextManager constructor.

        :param config: The configuration passed to the context manager.
        :type config: dict
        """
        self._config = config
        module_logger.debug("Get config {}".format(config))
        self._workspace = self._get_workspace()

    @staticmethod
    def _get_workspace():
        from azureml.core.workspace import Workspace
        from azureml.core.authentication import AzureMLTokenAuthentication

        try:
            # Load authentication scope environment variables
            subscription_id = os.environ['AZUREML_ARM_SUBSCRIPTION']
            resource_group = os.environ["AZUREML_ARM_RESOURCEGROUP"]
            workspace_name = os.environ["AZUREML_ARM_WORKSPACE_NAME"]
            experiment_name = os.environ["AZUREML_ARM_PROJECT_NAME"]
            run_id = os.environ["AZUREML_RUN_ID"]

            # Initialize an AMLToken auth, authorized for the current run
            token, token_expiry_time = AzureMLTokenAuthentication._get_initial_token_and_expiry()
            url = os.environ["AZUREML_SERVICE_ENDPOINT"]
            location = re.compile("//(.*?)\.").search(url).group(1)
        except KeyError as key_error:
            raise_from(RunEnvironmentException(), key_error)
        else:
            auth = AzureMLTokenAuthentication.create(token,
                                                     AzureMLTokenAuthentication._convert_to_datetime(
                                                         token_expiry_time),
                                                     url,
                                                     subscription_id,
                                                     resource_group,
                                                     workspace_name,
                                                     experiment_name,
                                                     run_id)
            # Disabling service check as this code executes in the remote context, without arm token.
            workspace_object = Workspace(subscription_id, resource_group, workspace_name,
                                         auth=auth, _location=location, _disable_service_check=True)
            return workspace_object


class DatasetContextManager(_CommonContextManager):
    """Manage the context for dataset download and mount actions. This class is not intended to be used directly."""

    def __init__(self, config):
        """Class DatasetContextManager constructor.

        :param config: The configuration passed to the context manager.
        :type config: dict
        """
        _log_and_print("Initialize DatasetContextManager.")
        super(self.__class__, self).__init__(config)
        self._mount_contexts = []

    def __enter__(self):
        """Download and mount datasets."""
        _log_and_print("Enter __enter__ of DatasetContextManager")
        for key, value in self._config.items():
            data_configuration = self._to_dataset_config(value)
            _log_and_print("Processing '{}'".format(key))

            if DatasetContextManager._is_download(data_configuration) or \
                    DatasetContextManager._is_mount(data_configuration):
                dataset = _Dataset.get_by_id(self._workspace, data_configuration.data_location.dataset.id)
                _log_and_print("Processing dataset {}".format(dataset))

                if isinstance(dataset, FileDataset):
                    # only file dataset can be downloaded or mount.
                    # The second part of the or statement below is to keep backwards compatibility until the execution
                    # service change has been deployed to all regions.
                    target_path = os.environ.get(data_configuration.environment_variable_name) or \
                        os.environ.get(data_configuration.environment_variable_name.upper())
                    overwrite = data_configuration.overwrite
                    if self._is_download(data_configuration):
                        _log_and_print("Downloading {} to {}".format(key, target_path))
                        dataset.download(target_path=target_path, overwrite=overwrite)
                        _log_and_print("Downloaded {} to {}".format(key, target_path))
                    else:
                        if not os.path.exists(target_path):
                            os.makedirs(target_path)
                        _log_and_print("Mounting {} to {}".format(key, target_path))
                        context_manager = dataset.mount(mount_point=target_path)
                        context_manager.__enter__()
                        _log_and_print("Mounted {} to {}".format(key, target_path))
                        self._mount_contexts.append(context_manager)
                    DatasetContextManager._update_env_var_if_single_file(
                        data_configuration.environment_variable_name, dataset)
                else:
                    _log_and_print("Mode is set to mount or download but the dataset is not a FileDataset. This "
                                   "should not happen, if you see this message please report this issue.")
        _log_and_print("Exit __enter__ of DatasetContextManager")

    def __exit__(self, *exc_details):
        """Unmount mounted datasets."""
        _log_and_print("Enter __exit__ of DatasetContextManager")
        for context in self._mount_contexts:
            _log_and_print("Unmounting {}.".format(context.mount_point))
            context.__exit__()
            _log_and_print("Finishing unmounting {}.".format(context.mount_point))
        _log_and_print("Exit __exit__ of DatasetContextManager")

    @staticmethod
    def _to_dataset_config(config):
        data_location_json = config.get("DataLocation", None)
        dataset_json = \
            data_location_json.get("Dataset", None) if data_location_json else None
        dataset_id = \
            dataset_json.get("Id") if dataset_json else None
        dataset = Dataset(dataset_id=dataset_id)
        data_location = DataLocation(dataset=dataset)
        create_output_directories = config.get('CreateOutputDirectories', False)
        mechanism = config.get("Mechanism", None).lower()
        environment_variable_name = config.get("EnvironmentVariableName", None)
        path_on_compute = config.get("PathOnCompute", None)
        overwrite = config.get("Overwrite", False)
        return Data(data_location=data_location,
                    create_output_directories=create_output_directories,
                    mechanism=mechanism,
                    environment_variable_name=environment_variable_name,
                    path_on_compute=path_on_compute,
                    overwrite=overwrite)

    @staticmethod
    def _is_download(data_configuration):
        return data_configuration.mechanism.lower() == 'download'

    @staticmethod
    def _is_mount(data_configuration):
        return data_configuration.mechanism.lower() == 'mount'

    @staticmethod
    def _update_env_var_if_single_file(env_name, dataset):
        if DatasetContextManager._is_single_file_no_transform(dataset):
            path = dataset.to_path()[0]
            os.environ[env_name] = os.environ[env_name].rstrip('/\\')
            os.environ[env_name] += path

            # the line below is here to keep backwards compatibility with data reference usage
            os.environ['AZUREML_DATAREFERENCE_{}'.format(env_name)] = os.environ[env_name]
            # the line below is to make sure run.input_datasets return the correct path
            os.environ[env_name.upper()] = os.environ[env_name]

    @staticmethod
    def _is_single_file_no_transform(dataset):
        steps = dataset._dataflow._get_steps()

        # if there is more than one step, we are going to naively assume that the resulting number of files is
        # nondeterministic
        if len(steps) > 1:
            return False

        first_step = steps[0]
        argument = first_step.arguments
        try:
            argument = argument.to_pod()
        except AttributeError:
            pass

        original_path = _get_path_from_step(first_step.step_type, argument)
        if not original_path:
            return False

        if http_pattern.match(original_path):
            url = urlparse(original_path)
            original_path = url.path

        temp_column = 'Temp Portable Path'
        dataflow = dataset._dataflow.take(1).add_column(
            dataprep().api.functions.get_portable_path(dataprep().api.expressions.col('Path')), temp_column, 'Path')
        path = dataflow.to_pandas_dataframe()[temp_column].values[0]

        return path.strip('/').endswith(original_path.replace('\\', '/').strip('/'))


class DatastoreContextManager(_CommonContextManager):
    """Manage the context for datastore upload and download actions. This class is not intended to be used directly."""

    def __init__(self, config):
        """Class DatastoreContextManager constructor.

        :param config: The configuration passed to the context manager.
        :type config: dict
        """
        module_logger.debug("Initialize DatastoreContextManager.")
        super(self.__class__, self).__init__(config)

    def __enter__(self):
        """Download files for datastore.

        :return:
        """
        module_logger.debug("Enter __enter__ function of datastore cmgr")
        for key, value in self._config.items():
            df_config = self._to_data_reference_config(value)
            if self._is_download(df_config):
                self._validate_config(df_config, key)
                ds = Datastore(workspace=self._workspace, name=df_config.data_store_name)
                target_path = df_config.data_store_name
                if df_config.path_on_compute:
                    target_path = os.path.join(df_config.data_store_name, df_config.path_on_compute)
                    # The target_path is always set using the data store name with no way
                    # for the user to overwrite this behavior. The user might attempt to use ../ in
                    # the path on compute as a solution but this throws an exception
                    # because the path is not normalized.
                    # Normalizing the path to allow the user to use up-level references.
                    target_path = os.path.normpath(target_path)
                ds.download(
                    target_path=target_path,
                    prefix=df_config.path_on_data_store,
                    overwrite=df_config.overwrite)
        module_logger.debug("Exit __enter__ function of datastore cmgr")

    def __exit__(self, *exc_details):
        """Upload files for datastore.

        :param exc_details:
        :return:
        """
        module_logger.debug("Enter __exit__ function of datastore cmgr")
        for key, value in self._config.items():
            df_config = self._to_data_reference_config(value)
            if self._is_upload(df_config):
                self._validate_config(df_config, key)
                ds = Datastore(workspace=self._workspace, name=df_config.data_store_name)
                if os.path.isdir(df_config.path_on_compute):
                    ds.upload(
                        src_dir=df_config.path_on_compute,
                        target_path=df_config.path_on_data_store,
                        overwrite=df_config.overwrite)
                elif os.path.isfile(df_config.path_on_compute):
                    ds.upload_files(
                        files=[df_config.path_on_compute],
                        target_path=df_config.path_on_data_store,
                        overwrite=df_config.overwrite)
        module_logger.debug("Exit __exit__ function of datastore cmgr")

    def _validate_config(self, data_reference, key):
        if not data_reference.data_store_name:
            raise UserErrorException("DataReference {} misses the datastore name".format(key))
        if self._is_upload(data_reference) and not data_reference.path_on_compute:
            raise UserErrorException("DataReference {} misses the relative path on the compute".format(key))

    @staticmethod
    def _to_data_reference_config(config):
        return DataReferenceConfiguration(
            datastore_name=config.get("DataStoreName", None),
            mode=config.get("Mode", "mount").lower(),
            path_on_datastore=config.get("PathOnDataStore", None),
            path_on_compute=config.get("PathOnCompute", None),
            overwrite=config.get("Overwrite", False))

    @staticmethod
    def _is_download(data_reference):
        return data_reference.mode.lower() == 'download'

    @staticmethod
    def _is_upload(data_reference):
        return data_reference.mode.lower() == 'upload'
