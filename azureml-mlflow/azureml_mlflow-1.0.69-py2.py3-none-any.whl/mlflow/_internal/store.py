# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""**AzureMLflowStore** provides a class to read and record run metrics and artifacts on Azure via MLflow."""

import logging
import os
import time
from functools import wraps
from six.moves.urllib import parse

import mlflow
from mlflow.store.rest_store import RestStore
from mlflow.store import SEARCH_MAX_RESULTS_DEFAULT
from mlflow.utils.rest_utils import MlflowHostCreds
from mlflow.utils.databricks_utils import get_databricks_host_creds
from mlflow.tracking.utils import get_db_profile_from_uri
from mlflow.exceptions import RestException
from mlflow.entities import ViewType

from azureml.core.authentication import AzureMLTokenAuthentication
from azureml._restclient.clientbase import DEFAULT_BACKOFF, DEFAULT_RETRIES
from azureml._restclient.run_client import RunClient
from azureml._restclient.workspace_client import WorkspaceClient
from .utils import (execute_func, handle_exception, get_aml_experiment_name,
                    tracking_uri_decomp, _SUB_ID, _RES_GRP, _WS_NAME)

from .authentication import DBTokenAuthentication
from .hybrid_service_context import HybridServiceContext

logger = logging.getLogger(__name__)

PARAM_PREFIX = "azureml.param."

_EXPERIMENT_NAME_ENV_VAR = "MLFLOW_EXPERIMENT_NAME"
_MLFLOW_RUN_ID_ENV_VAR = "MLFLOW_RUN_ID"


class AzureMLRestStore(RestStore):
    """
    Client for a remote tracking server accessed via REST API calls.

    :param service_context: Service context for the AzureML workspace
    :type service_context: azureml._restclient.service_context.ServiceContext
    """

    def __init__(self, service_context, host_creds=None):
        """
        Construct an AzureMLRestStore object.

        :param service_context: Service context for the AzureML workspace
        :type service_context: azureml._restclient.service_context.ServiceContext
        """
        logger.debug("Initializing the AzureMLRestStore")
        self.service_context = service_context
        self.get_host_creds = host_creds if host_creds is not None else self.get_host_credentials
        super(AzureMLRestStore, self).__init__(self.get_host_creds)
        self.workspace_client = WorkspaceClient(service_context)

    def get_host_credentials(self):
        """
        Construct a MlflowHostCreds to be used for obtaining fresh credentials and the host url.

        :return: The host and credential for rest calls.
        :rtype: mlflow.utils.rest_utils.MlflowHostCreds
        """
        return MlflowHostCreds(
            self.service_context._get_run_history_url() +
            "/history/v1.0" + self.service_context._get_workspace_scope(),
            token=self.service_context.get_auth().get_authentication_header()["Authorization"][7:])

    @wraps(RestStore._call_endpoint)
    def _call_endpoint(self, *args, **kwargs):
        total_retry = DEFAULT_RETRIES
        backoff = DEFAULT_BACKOFF
        for i in range(total_retry):
            try:
                return super(AzureMLRestStore, self)._call_endpoint(*args, **kwargs)
            except RestException as rest_exception:
                more_retries_left = i < total_retry - 1
                is_throttled = rest_exception.json.get("error", {"code": 0}).get("code") == "RequestThrottled"
                if more_retries_left and is_throttled:
                    logger.debug("There were too many requests. Try again soon.")
                    self._wait_for_retry(backoff, i, total_retry)
                else:
                    raise

    @classmethod
    def _wait_for_retry(cls, back_off, left_retry, total_retry):
        delay = back_off * 2 ** (total_retry - left_retry - 1)
        time.sleep(delay)

    def _update_authentication(self, run_id, experiment_name):
        """
        Helper function for initializing the AzureMLTokenAuthentication class
        to avoid expiring AAD tokens. Also initializes the AzureML token refresher.

        :param run_id: The run id for the Run.
        :type run_id: str
        :param experiment_name: The name of the experiment.
        :type experiment_name: str
        """
        run_client = RunClient(self.service_context, experiment_name, run_id)
        token = run_client.get_token().token
        auth = AzureMLTokenAuthentication.create(
            azureml_access_token=token,
            expiry_time=None,
            host=self.service_context._get_run_history_url(),
            subscription_id=self.service_context.subscription_id,
            resource_group_name=self.service_context.resource_group_name,
            workspace_name=self.service_context.workspace_name,
            experiment_name=experiment_name,
            run_id=run_id
        )
        self.service_context._authentication = auth

    @wraps(RestStore.create_run)
    def create_run(self, *args, **kwargs):
        auth = self.service_context.get_auth()
        logger.debug("Creating an Mlflow run with {} auth token".format(auth.__class__.__name__))
        run = super(AzureMLRestStore, self).create_run(*args, **kwargs)
        if not isinstance(auth, AzureMLTokenAuthentication) and _EXPERIMENT_NAME_ENV_VAR in os.environ:
            self._update_authentication(run.info.run_id, os.environ[_EXPERIMENT_NAME_ENV_VAR])

        return run

    def get_experiment_by_name(self, experiment_name, *args, **kwargs):
        """
        Fetch the experiment by name from the backend store.

        :param experiment_name: Name of experiment

        :return: A single :py:class:`mlflow.entities.Experiment` object if it exists.
        """
        if len(args) + len(kwargs) > 0:
            logger.debug("Found unsupported inputs to {}.get_experiment_by_name: args {} and kwargs {}. "
                         "The inputs will be ignored.".format(self.__class__.__name__, args, kwargs))
        experiment_id = None
        try:
            azureml_experiment = self.workspace_client.get_experiment(experiment_name)
            experiment_id = azureml_experiment.experiment_id
        except Exception as e:
            logger.debug("Could not load experiment '{}' with exception: {}".format(experiment_name, e))
        return None if experiment_id is None else self.get_experiment(experiment_id)


class AdbAzuremlRestStore(RestStore):

    def __init__(self, tracking_uri):
        """Construct an AdbAzuremlRestStore object."""
        self._tracking_uri = tracking_uri

        self.adb_store = self.get_db_store()
        self.aml_store = self.get_aml_store()
        self.stores = [self.adb_store, self.aml_store]
        self.reader_store = self.stores[0]
        self.get_host_creds = self.get_host_credentials
        super(AdbAzuremlRestStore, self).__init__(self.get_host_creds)

    def get_db_store(self):
        tracking_uri = mlflow.tracking.get_tracking_uri()
        profile = get_db_profile_from_uri("databricks")
        logger.info("tracking uri: {} and profile: {}".format(tracking_uri, profile))
        return RestStore(lambda: get_databricks_host_creds(profile))

    def get_aml_store(self):
        tracking_uri = mlflow.tracking.get_tracking_uri()
        logger.info("tracking uri: {}".format(tracking_uri))
        parsed_url = parse.urlparse(tracking_uri)
        region = parsed_url.netloc
        parsed_path = tracking_uri_decomp(parsed_url.path)
        subscription_id = parsed_path[_SUB_ID]
        resource_group_name = parsed_path[_RES_GRP]
        workspace_name = parsed_path[_WS_NAME]

        token = self.get_host_credentials().token
        auth = DBTokenAuthentication(token)
        service_context = HybridServiceContext(subscription_id, resource_group_name,
                                               workspace_name, None, auth, region)
        return AzureMLRestStore(service_context=service_context,
                                host_creds=self.get_aml_host_credentials)

    def get_host_credentials(self):
        return self.adb_store.get_host_creds()

    def get_aml_host_credentials(self):
        """Construct a MlflowHostCreds to be used for obtaining fresh credentials."""
        return MlflowHostCreds(
            self.aml_store.service_context._get_run_history_url() +
            "/history/v1.0" + self.aml_store.service_context._get_workspace_scope(),
            token=self.aml_store.service_context.get_auth().get_authentication_header()["Authorization"][7:])

    def create_experiment(self, *args, **kwargs):
        exp_name = kwargs['name']
        operation = "create experiment with name {}.".format(exp_name)
        try:
            exp = self.adb_store.create_experiment(*args, **kwargs)
        except Exception as e:
            handle_exception(operation, self.adb_store, e)

        kwargs['name'] = get_aml_experiment_name(exp_name)
        try:
            experiment = self.aml_store.get_experiment_by_name(kwargs['name'])
            exp_id = experiment.experiment_id if experiment else None
            if exp_id is None:
                self.aml_store.create_experiment(*args, **kwargs)
        except Exception as e:
            handle_exception(operation, self.aml_store, e)

        return exp

    def get_experiment(self, experiment_id):
        return self.reader_store.get_experiment(experiment_id)

    def get_experiment_by_name(self, experiment_name):
        return self.reader_store.get_experiment_by_name(experiment_name)

    def list_experiments(self, view_type=ViewType.ACTIVE_ONLY):
        return self.reader_store.list_experiments(view_type)

    def list_run_infos(self, experiment_id, run_view_type):
        return self.reader_store.list_run_infos(experiment_id, run_view_type)

    def search_runs(self, experiment_ids, filter_string, run_view_type,
                    max_results=SEARCH_MAX_RESULTS_DEFAULT, order_by=None, page_token=None):
        # This gives TypeError: search_runs() takes from 4 to 5 positional arguments but 7 were given ??
        # return self.reader_store.search_runs(experiment_ids, filter_string, run_view_type,
        #                                      max_results, order_by, page_token)
        return self.reader_store.search_runs(experiment_ids, filter_string, run_view_type)

    def create_run(self, experiment_id, user_id, start_time, tags):
        operation = "create run"
        try:
            run = self.adb_store.create_run(experiment_id, user_id, start_time, tags)
            experiment_name = self.adb_store.get_experiment(experiment_id)._name
        except Exception as e:
            handle_exception(operation, self.adb_store, e)

        experiment_name = get_aml_experiment_name(experiment_name)
        try:
            run_dto = create_mlflow_run(self.aml_store.service_context, experiment_name,
                                        run.info.run_id, user_id, start_time, tags)
            self.aml_store.get_run(run_dto.run_id)
        except Exception as e:
            handle_exception(operation, self.aml_store, e)

        return run

    def get_run(self, run_id):
        reader_run = self.reader_store.get_run(run_id)
        reader_run._info._artifact_uri = reader_run.info.artifact_uri.replace("dbfs", "adbazureml", 1)
        return reader_run

    def get_metric_history(self, run_id, metric_key):
        return self.reader_store.get_metric_history(run_id, metric_key)

    def update_run_info(self, *args, **kwargs):
        operation = "update run info"
        execute_func(lambda store, *args, **kwargs: store.update_run_info(*args, **kwargs),
                     self.stores, operation, *args, **kwargs)

    def log_metric(self, *args, **kwargs):
        operation = "log_metric"
        execute_func(lambda store, *args, **kwargs: store.log_metric(*args, **kwargs),
                     self.stores, operation, *args, **kwargs)

    def log_param(self, *args, **kwargs):
        operation = "log_param"
        execute_func(lambda store, *args, **kwargs: store.log_param(*args, **kwargs),
                     self.stores, operation, *args, **kwargs)

    def set_tag(self, *args, **kwargs):
        operation = "set_tag"
        execute_func(lambda store, *args, **kwargs: store.set_tag(*args, **kwargs),
                     self.stores, operation, *args, **kwargs)


def create_mlflow_run(service_context, experiment_name, run_id, user_id, start_time, tags):
    from azureml._restclient.run_client import RunClient
    from azureml._restclient.models.create_run_dto import CreateRunDto

    client = RunClient(service_context, experiment_name, run_id)
    client.create_run(run_id=run_id, target="sdk", run_name="run_{}".format(run_id))
    client.post_event_start()
    tags = {tag.key: tag.value for tag in tags}
    tags["mlflow.user"] = user_id
    sanitized_tags = {}
    for key, val in tags.items():
        if not isinstance(val, (str, type(None))):
            sanitized_tags[key] = str(val)
        else:
            sanitized_tags[key] = val
    create_run_dto = CreateRunDto(run_id=run_id, tags=sanitized_tags)
    return client.patch_run(create_run_dto)
