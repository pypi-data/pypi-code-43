# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ---------------------------------------------------------
"""Access workspace client"""
import copy

from azureml._restclient.models import ModifyExperimentDto

from .clientbase import ClientBase, PAGINATED_KEY

from ._odata.constants import ORDER_BY_CREATEDTIME_EXPRESSION
from .utils import _generate_client_kwargs, _validate_order_by
from .exceptions import ServiceException
from .models.error_response import ErrorResponseException


class WorkspaceClient(ClientBase):
    """
    Run History APIs

    :param host: The base path for the server to call.
    :type host: str
    :param auth: Client authentication
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param subscription_id:
    :type subscription_id: str
    :param resource_group_name:
    :type resource_group_name: str
    :param workspace_name:
    :type workspace_name: str
    """

    def __init__(self, service_context, host=None, **kwargs):
        """
        Constructor of the class.
        """
        self._service_context = service_context
        self._override_host = host
        self._workspace_arguments = [self._service_context.subscription_id,
                                     self._service_context.resource_group_name,
                                     self._service_context.workspace_name]
        super(WorkspaceClient, self).__init__(**kwargs)

        self._custom_headers = {}

    @property
    def auth(self):
        return self._service_context.get_auth()

    def get_rest_client(self, user_agent=None):
        """get service rest client"""
        return self._service_context._get_run_history_restclient(
            host=self._override_host, user_agent=user_agent)

    def get_cluster_url(self):
        """get service url"""
        return self._host

    def get_workspace_uri_path(self):
        return self._service_context._get_workspace_scope()

    def _execute_with_workspace_arguments(self, func, *args, **kwargs):
        return self._execute_with_arguments(func, copy.deepcopy(self._workspace_arguments), *args, **kwargs)

    def _execute_with_arguments(self, func, args_list, *args, **kwargs):
        if not callable(func):
            raise TypeError('Argument is not callable')

        if self._custom_headers:
            kwargs["custom_headers"] = self._custom_headers

        if args:
            args_list.extend(args)
        is_paginated = kwargs.pop(PAGINATED_KEY, False)
        try:
            if is_paginated:
                return self._call_paginated_api(func, *args_list, **kwargs)
            else:
                return self._call_api(func, *args_list, **kwargs)
        except ErrorResponseException as e:
            raise ServiceException(e)

    def list_experiments(self, last=None, order_by=None):
        """
        list all experiments
        :return: a generator of ~_restclient.models.ExperimentDto
        """

        kwargs = {}
        if last is not None:
            order_by_expression = _validate_order_by(order_by) if order_by else [ORDER_BY_CREATEDTIME_EXPRESSION]
            kwargs = _generate_client_kwargs(top=last, orderby=order_by_expression)
            # TODO: Doesn't work
            raise NotImplementedError("Cannot limit experiment list")

        return self._execute_with_workspace_arguments(self._client.experiment.list,
                                                      is_paginated=True,
                                                      **kwargs)

    def get_experiment(self, experiment_name, is_async=False):
        """
        list all experiments in a workspace
        :param experiment_name: experiment name (required)
        :type experiment_name: str
        :param is_async: execute request asynchronously
        :type is_async: bool
        :return:
            If is_async parameter is True,
            the request is called asynchronously.
            The method returns azureml._async_task.AsyncTask object
            If parameter is_async is False or missing,
            return: ~_restclient.models.ExperimentDto
        """

        return self._execute_with_workspace_arguments(self._client.experiment.get,
                                                      experiment_name=experiment_name,
                                                      is_async=is_async)

    def get_experiment_by_id(self, experiment_id, is_async=False):
        """
        get experiment by id
        :param experiment_id: experiment id (required)
        :type experiment_id: str
        :param is_async: execute request asynchronously
        :type is_async: bool
        :return:
            If is_async parameter is True,
            the request is called asynchronously.
            The method returns azureml._async_task.AsyncTask object
            If parameter is_async is False or missing,
            return: ~_restclient.models.ExperimentDto
        """

        return self._execute_with_workspace_arguments(self._client.experiment.get_by_id,
                                                      experiment_id=experiment_id,
                                                      is_async=is_async)

    def archive(self, experiment_id, caller=None, custom_headers=None, is_async=False):
        """
        Archive the experiment
        :param experiment_id: experiment id (required)
        :type experiment_id: str
        :param is_async: execute request asynchronously
        :type is_async: bool
        :param caller: caller function name (optional)
        :type caller: optional[string]
        :param custom_headers: headers that will be added to the request (optional)
        :type custom_headers: optional[dict]
        :return:
            the return type is based on is_async parameter.
            If is_async parameter is True,
            the request is called asynchronously.
        rtype: ~_restclient.models.ExperimentDto (is_async is False) or
            azureml._async.AsyncTask (is_async is True)
        """
        modify_experiment_dto = ModifyExperimentDto(archive=True)
        return self.update_experiment(experiment_id, modify_experiment_dto, caller, custom_headers, is_async)

    def unarchive(self, experiment_id, caller=None, custom_headers=None, is_async=False):
        """
        Unarchive the experiment
        :param experiment_id: experiment id (required)
        :type experiment_id: str
        :param is_async: execute request asynchronously
        :type is_async: bool
        :param caller: caller function name (optional)
        :type caller: optional[string]
        :param custom_headers: headers that will be added to the request (optional)
        :type custom_headers: optional[dict]
        :return:
            the return type is based on is_async parameter.
            If is_async parameter is True,
            the request is called asynchronously.
        rtype: ~_restclient.models.ExperimentDto (is_async is False) or
            azureml._async.AsyncTask (is_async is True)
        """
        modify_experiment_dto = ModifyExperimentDto(archive=False)
        return self.update_experiment(experiment_id, modify_experiment_dto, caller, custom_headers, is_async)

    def update_experiment(self, experiment_id, modify_experiment_dto,
                          caller=None, custom_headers=None, is_async=False):
        """
        Update the experiment
        :param experiment_id: experiment id (required)
        :type experiment_id: str
        :param modify_experiment_dto: modify experiment dto
        :type modify_experiment_dto: ModifyExperimentDto
        :param is_async: execute request asynchronously
        :type is_async: bool
        :param caller: caller function name (optional)
        :type caller: optional[string]
        :param custom_headers: headers that will be added to the request (optional)
        :type custom_headers: optional[dict]
        :return:
            the return type is based on is_async parameter.
            If is_async parameter is True,
            the request is called asynchronously.
        rtype: ~_restclient.models.ExperimentDto (is_async is False) or
            azureml._async.AsyncTask (is_async is True)
        """
        kwargs = _generate_client_kwargs(
            modify_experiment_dto=modify_experiment_dto,
            is_async=is_async, caller=caller, custom_headers=custom_headers)
        return self._execute_with_workspace_arguments(
            self._client.experiment.update, experiment_id=experiment_id, **kwargs)
