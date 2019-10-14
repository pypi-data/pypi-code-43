# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import sys
import traceback


class AzureMLException(Exception):
    """
    The base class for all Azure ML exceptions.

    This class extends the Python Exception class. If you are trying to catch only Azure ML exceptions,
    then catch them with this class.

    .. remarks::

        The following code example shows how to handle the :class:`azureml.exceptions.WebserviceException`,
        which is a subclass of AzureMLException. In the code, if the check of the service fails, then
        the WebserviceException is handled and a message can be printed.

        .. code-block:: python

            from azureml.core.webservice import AciWebservice, Webservice
            from azureml.exceptions import WebserviceException

            deployment_config = AciWebservice.deploy_configuration(cpu_cores=1, memory_gb=1)
            aci_service_name = 'aciservice1'

            try:
                # if you want to get existing service below is the command
                # since aci name needs to be unique in subscription deleting existing aci if any
                # we use aci_service_name to create azure aci
                service = Webservice(ws, name=aci_service_name)
                if service:
                    service.delete()
            except WebserviceException as e:
                print()

            service = Model.deploy(ws, aci_service_name, [model], inference_config, deployment_config)

            service.wait_for_deployment(True)
            print(service.state)

        Full sample is available from
        https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/deployment/deploy-to-cloud/model-register-and-deploy.ipynb


    :param exception_message: A message describing the error.
    :type exception_message: str
    :param inner_exception: An optional error message, for example, from a previously handled exception.
    :type inner_exception: str
    :param target: The name of the element that caused the exception to be thrown.
    :type target: str
    :param details: Any additional information for the error, such as other error responses or stacktraces.
    :type details: builtin.list(str)
    """

    def __init__(self, exception_message, inner_exception=None, target=None, details=None, **kwargs):
        Exception.__init__(self, exception_message, **kwargs)
        self._exception_message = exception_message
        self._inner_exception = inner_exception
        self._exc_info = sys.exc_info()
        self._target = target
        self._details = details

        """
        Initialize a new instance of AzureMLException.

        :param exception_message: A message describing the error.
        :type exception_message: str
        :param inner_exception: An optional error message, for example, from a previously handled exception.
        :type inner_exception: str
        :param target: The name of the element that caused the exception to be thrown.
        :type target: str
        :param details: Any additional information for the error, such as other error responses or stacktraces.
        :type details: builtin.list(str)
        """

    def __repr__(self):
        """Return the string representation of the AzureMLException object.

        :return: String representation of the AzureMLException object
        :rtype: str
        """
        return "{}:\n\tMessage: {}\n\tInnerException {}\n\tErrorResponse \n{}".format(
            self.__class__.__name__,
            self.message,
            self.inner_exception,
            self._serialize_json(indent=4))

    def __str__(self):
        """Return the string representation of the AzureMLException."""
        return self.__repr__()

    @property
    def message(self):
        """Return the error message.

        :return: The error message.
        :rtype: str
        """
        return self._exception_message

    @message.setter
    def message(self, value):
        self._exception_message = value

    @property
    def inner_exception(self):
        """Return the inner exception message.

        :return: The inner exception message.
        :rtype: str
        """
        return self._inner_exception

    @inner_exception.setter
    def inner_exception(self, value):
        self._inner_exception = value

    def print_stacktrace(self):
        traceback.print_exception(*self._exc_info)

    def _serialize_json(self, indent=None):
        """
        Serialize this exception as an ErrorResponse JSON.
        :return: A JSON string representation of the exception.
        :rtype: str
        """
        error_ret = {}
        error_out = {}
        for super_class in self.__class__.mro():
            if super_class.__name__ == AzureMLException.__name__:
                break
            try:
                error_code = getattr(super_class, '_error_code')
                if error_out != {}:
                    # Flatten the tree in case we have something like System > System > System > System
                    prev_code = error_out.get('code')
                    if prev_code is None or error_code != prev_code:
                        error_out = {"code": error_code, "inner_error": error_out}
                else:
                    error_out = {"code": error_code}
            except AttributeError:
                break

        error_out['message'] = self._exception_message
        if self._target is not None:
            error_out['target'] = self._target
        if self._details is not None:
            error_out['details'] = self._details
        error_ret['error'] = error_out

        return json.dumps(error_ret, indent=indent)

    def _contains_code(self, code_hierarchy):
        """
        Determine whether this error exists within the hierarchy provided.
        :param code_hierarchy: List of strings sorted by hierarchy.
        :return: True if error exists in hierarchy; otherwise, False.
        :rtype: bool
        """
        error_response = json.loads(self._serialize_json())
        inner_error = error_response.get('error')
        response_hierarchy = []
        while inner_error is not None:
            response_hierarchy.append(inner_error.get('code'))
            inner_error = inner_error.get('inner_error')

        # Compare only the first K codes, allow more granular codes to be defined
        return code_hierarchy == response_hierarchy[:len(code_hierarchy)]
