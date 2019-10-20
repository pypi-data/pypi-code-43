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

import os
from collections import namedtuple
from unittest.mock import patch

import click.testing

from . import azure

# Some of the test cases use patching for mocking third party dependencies.
# Because the unittest.mock.patch function expects those patched objects to
# be present as (then unused) function arguments, this pylint warning will
# be disabled.
# pylint: disable=unused-argument

EnvironmentVariable = namedtuple("EnvironmentVariable", ["env", "arg", "value"])

ENV_VARS = [
    EnvironmentVariable("AZURE_CLIENT_ID", "--client-id", "Azure_Client_Id"),
    EnvironmentVariable(
        "AZURE_CLIENT_SECRET", "--client-secret", "Azure_Client_Secret"
    ),
    EnvironmentVariable(
        "AZURE_SUBSCRIPTION_ID", "--subscription-id", "Azure_Subscription_Id"
    ),
    EnvironmentVariable("AZURE_TENANT_ID", "--tenant-id", "Azure_Tenant_Id"),
]


def test_azure_without_prefix():
    """
    This test case verifies that the azure provider will not run when no
    prefix argument is provided.
    """
    expected_exit_code = 2
    expected_output = (
        "Usage: azure [OPTIONS]\n"
        'Try "azure --help" for help.\n'
        "\n"
        'Error: Missing option "--prefix".\n'
    )

    args = []

    runner = click.testing.CliRunner()
    actual = runner.invoke(azure.azure, args=args)

    assert actual.exit_code == expected_exit_code
    assert actual.output == expected_output


def test_azure_without_environment_variables():
    """
    This test case verifies that the azure provider will not run when the
    necessary environment variables are not set.
    """
    expected_exit_code = 1
    expected_output = "azure provider is missing the 'AZURE_CLIENT_ID'.\n"

    runner = click.testing.CliRunner()
    actual = runner.invoke(azure.azure, args=["--prefix=test"])

    assert actual.exit_code == expected_exit_code
    assert actual.output == expected_output


@patch("azure.common.credentials.ServicePrincipalCredentials")
@patch("azure.mgmt.resource.ResourceManagementClient")
def test_azure_with_prefix_and_environment_variables(cred, client):
    """
    This test case verifies that the azure provider will run properly if all
    necessary environment variables are set.

    In order to avoid calls to the Microsoft Azure API, both external
    dependencies are patched as mock objects.
    """
    expected_exit_code = 0
    expected_output = f"Found no deletable resource groups for prefix test.\n"

    args = ["--prefix=test"]

    with patch.dict(os.environ, {env.env: env.value for env in ENV_VARS}):
        runner = click.testing.CliRunner()
        actual = runner.invoke(azure.azure, args=args)

        assert actual.exit_code == expected_exit_code
        assert actual.output == expected_output


def test_azure_with_permutations_of_missing_environment_variables(subtests):
    """
    This test case verifies that the azure provider will not run when at least
    one of the necessary environment variables is not set if called without
    additional command line arguments.
    """
    for env_var in ENV_VARS:
        expected_exit_code = 1
        expected_output = f"azure provider is missing the '{env_var.env}'.\n"

        args = ["--prefix=test"]
        subset = {var.env: var.value for var in ENV_VARS if var != env_var}

        with patch.dict(os.environ, subset):
            runner = click.testing.CliRunner()
            actual = runner.invoke(azure.azure, args=args)

            with subtests.test(msg=f"Testing without {env_var} being set"):
                assert actual.exit_code == expected_exit_code
                assert actual.output == expected_output


@patch("azure.common.credentials.ServicePrincipalCredentials")
@patch("azure.mgmt.resource.ResourceManagementClient")
def test_azure_with_prefix_and_command_line_arguments(cred, client):
    """
    This test case verifies that the azure provider will run properly if all
    necessary command line arguments are provided.

    In order to avoid calls to the Microsoft Azure API, both external
    dependencies are patched as mock objects.
    """
    expected_exit_code = 0
    expected_output = f"Found no deletable resource groups for prefix test.\n"

    args = ["--prefix=test"] + [f"{env.arg}={env.value}" for env in ENV_VARS]

    with patch.dict(os.environ, {}):
        runner = click.testing.CliRunner()
        actual = runner.invoke(azure.azure, args=args)

        assert actual.exit_code == expected_exit_code
        assert actual.output == expected_output


def test_azure_without_env_vars_and_permutations_of_missing_arguments(subtests):
    """
    This test case verifies that the azure provider will not run when the
    necessary environment variables are not set and at least one of the
    necessary command line arguments is not provided.
    """
    for env_var in ENV_VARS:
        with patch.dict(os.environ, {}):
            expected_exit_code = 1
            expected_output = f"azure provider is missing the '{env_var.env}'.\n"

            subset = {var.arg: var.value for var in ENV_VARS if var != env_var}
            args = ["--prefix=test"] + [f"{k}={v}" for k, v in subset.items()]

            runner = click.testing.CliRunner()
            actual = runner.invoke(azure.azure, args=args)

            with subtests.test(msg=f"Testing without {env_var} being set"):
                assert actual.exit_code == expected_exit_code
                assert actual.output == expected_output


@patch("azure.common.credentials.ServicePrincipalCredentials")
@patch("azure.mgmt.resource.ResourceManagementClient")
def test_azure_with_one_missing_env_var_and_related_argument(cred, client, subtests):
    """
    This test case verifies that the azure provider will run properly if all
    but one environment variable is set and the missing value is provided
    as command line argument.

    In order to avoid calls to the Microsoft Azure API, both external
    dependencies are patched as mock objects.
    """
    for env_var in ENV_VARS:
        subset = {env.env: env.value for env in ENV_VARS if env != env_var}

        with patch.dict(os.environ, subset):
            expected_exit_code = 0
            expected_output = f"Found no deletable resource groups for prefix test.\n"

            args = ["--prefix=test", f"{env_var.arg}={env_var.value}"]

            runner = click.testing.CliRunner()
            actual = runner.invoke(azure.azure, args=args)

            with subtests.test(msg=f"Testing with {env_var} being set as argument"):
                assert actual.exit_code == expected_exit_code
                assert actual.output == expected_output
