"""
agipy enables you to destroy cloud infrastructure in a hurry.
Copyright (C) 2019  Nils Müller<shimst3r@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
"""
import concurrent.futures
import os
import sys

import click
from azure.common import credentials  # pylint: disable=no-name-in-module
from azure.mgmt import resource  # pylint: disable=no-name-in-module
from msrestazure.azure_exceptions import CloudError


class AzureProvider:
    """
    AzureProvider implements functionality to delete resources and resource
    groups on Microsoft Azure's public cloud infrastructure.
    """

    def __init__(self):
        self.client = self._setup_azure_client()

    @property
    def resource_groups(self):
        """
        resource_groups returns a list of resource groups for the given client.
        """
        return list(self.client.resource_groups.list())

    def delete(self, prefix: str):
        """
        delete connects to the Azure public cloud and deletes all
        resources and resource groups.
        """
        if not prefix:
            click.echo("Cannot delete resource groups without empty prefix.")
            sys.exit(1)
        self._delete_resource_groups_by_prefix(prefix=prefix)

    def _setup_azure_client(self) -> resource.ResourceManagementClient:
        """
        _setup_azure_client creates a ResourceManagementClient based on the
        environment variables.
        """
        try:
            client_id = os.environ["AZURE_CLIENT_ID"]
            client_secret = os.environ["AZURE_CLIENT_SECRET"]
            subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
            tenant_id = os.environ["AZURE_TENANT_ID"]
        except KeyError as error:
            click.echo(error)
            sys.exit(1)
        else:
            cred = credentials.ServicePrincipalCredentials(
                client_id=client_id, secret=client_secret, tenant=tenant_id
            )
            client = resource.ResourceManagementClient(
                credentials=cred, subscription_id=subscription_id
            )

            return client

    def _delete_resource_group_by_name(self, rg_name: str):
        """
        _delete_resource_group_by_name deletes a resource group based on
        its name.
        """
        awaitable = self.client.resource_groups.delete(rg_name)

        try:
            awaitable.wait()
        except CloudError as error:
            click.echo(error.message)
        else:
            click.echo(f"Succesfully deleted resource group {rg_name}.")

    def _delete_resource_groups_by_prefix(self, prefix: str):
        """
        _delete_resource_groups_by_prefix deletes all resource groups for a
        given subscription based on a given prefix.
        """
        deletables = [
            rgx for rgx in self.resource_groups if rgx.name.startswith(prefix)
        ]

        if not deletables:
            click.echo(f"Found no deletable resource groups for prefix {prefix}.")
            return

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for rgx in deletables:
                click.echo(
                    f"Found deletable resource group {rgx.name}. Initialise deletion."
                )
                executor.submit(self._delete_resource_group_by_name, rgx.name)

        click.echo(
            f"Succesfully deleted {len(deletables)} resource groups for prefix {prefix}."
        )
