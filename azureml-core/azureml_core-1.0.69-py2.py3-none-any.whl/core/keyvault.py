# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Keyvault module manages the secrets stored in the keyvault of the AzureML Workspace.

This module provides convenient methods for adding, retrieving, deleting and listing secrets
from the keyvault.
"""
import logging
from azureml._restclient.secrets_client import SecretsClient
module_logger = logging.getLogger(__name__)


class Keyvault(object):
    """Keyvault class to manage secrets stored in the keyvault of the AzureML Workspace.

    This module provides convenient methods for setting, retrieving, deleting and listing secrets
    from the keyvault.

    :param workspace: The workspace
    :type workspace: azureml.core.Workspace
    """

    def __init__(self, workspace):
        """Class Keyvault constructor."""
        self.workspace = workspace

    def set_secret(self, name, value):
        """Add a secret in the keyvault associated with your workspace.

        :param name:
        :type name: str
        :param value:
        :type value: str
        :return:
        :rtype: None
        """
        Keyvault._client(self.workspace)._add_secret(name, value)

    def set_secrets(self, secrets_batch):
        """Add the dictionary of secrets into the keyvault associated with your workspace.

        :param secrets_batch:
        :type secrets_batch: Dictionary of secret names and values to be added
        :return:
        :rtype: None
        """
        Keyvault._client(self.workspace)._add_secrets(secrets_batch)

    def get_secret(self, name):
        """Return the secret value for a given name.

        :param name:
        :type name: str
        :return: Returns the secret value for a specified secret name
        :rtype: str
        """
        return Keyvault._client(self.workspace)._get_secret(name)

    def get_secrets(self, secrets):
        """Return the secret values for a given list of secret names.

        :param secrets:
        :type secrets: List of secret names to retrieve the values for
        :return: Returns a dictionary of found and not found secrets
        :rtype: dict{str: str}
        """
        return Keyvault._client(self.workspace)._get_secrets(secrets)

    def delete_secret(self, name):
        """Delete the secret.

        :param name:
        :type name: str
        :return:
        :rtype: None
        """
        Keyvault._client(self.workspace)._delete_secret(name)

    def delete_secrets(self, secrets):
        """Delete the list of secrets from your workspace.

        :param secrets_batch:
        :type secrets_batch: List of secrets to delete
        :return:
        :rtype: None
        """
        Keyvault._client(self.workspace)._delete_secrets(secrets)

    def list_secrets(self):
        """Return the list of secret names from your workspace.

        :return: Returns the List of dictionary of secret names with format {name : "secretName"}
        :rtype: List[str]
        """
        return Keyvault._client(self.workspace)._list_secrets()

    @staticmethod
    def _client(workspace):
        """Get a client.

        :return: Returns the client
        :rtype: SecretsClient
        """
        secrets_client = SecretsClient(workspace.service_context)
        return secrets_client
