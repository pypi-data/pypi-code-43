# Copyright 2019 Genymobile
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
gmsaas errors
"""
import json

from enum import Enum
import click
from .logger import LOGGER
from .model.instanceinfo import InstanceState, is_instance_starting, is_instance_stopping


class ExitCode(Enum):
    """
    Exit codes used by gmsaas
    """

    NO_ERROR = 0
    DEFAULT_ERROR = 1  # Default of ClickException class
    RESERVED = 2  # Used by click's UsageError class
    AUTHENTICATION_ERROR = 3
    API_ERROR = 4
    INVALID_JSON_ERROR = 5
    CONFIGURATION_ERROR = 6
    PACKAGE_ERROR = 7
    COMPATIBILITY_ERROR = 8
    UNREACHABLE_ERROR = 9
    INSTANCE_ERROR = 10
    ADBTUNNEL_BUSY_PORT_ERROR = 11
    ADBTUNNEL_GENERIC_ERROR = 12
    ADBTUNNEL_DIFFERENT_PORT_ERROR = 13
    ADBTUNNEL_INSTANCE_NOT_READY = 14
    REQUEST_ERROR = 15
    LOGZIP_ERROR = 16


class ApiErrorCode:
    """
    Error codes return by the API
    """

    BAD_USERNAME_PASSWORD = "BAD_USERNAME_PASSWORD"
    USER_NOT_ENABLED = "USER_NOT_ENABLED"


def echo_exception(exception, extra_message=None):
    """
    Print exception in stderr

    Exception message is also logged as well as extra_message and exit code.
    """
    LOGGER.error(exception.message)
    if extra_message:
        LOGGER.error(extra_message)
    LOGGER.info("==== STOP exit code: %d (%s) ====", exception.exit_code, ExitCode(exception.exit_code))
    click.echo(exception.message, err=True)


class AuthenticationError(click.ClickException):
    """
    Authentication Error
    """

    def __init__(self, status_code, message):
        output_message = "Error: {} {}".format(status_code, message)
        try:
            response = json.loads(message)
            code = response.get("code")
            if code == ApiErrorCode.BAD_USERNAME_PASSWORD:
                output_message = "Error: create an account or retrieve your password at https://cloud.geny.io."
            elif code == ApiErrorCode.USER_NOT_ENABLED:
                output_message = "Error: your account is disabled. Please contact your organization administrator."
        except Exception:
            pass

        click.ClickException.__init__(self, output_message)
        self.exit_code = ExitCode.AUTHENTICATION_ERROR.value

    def show(self, file=None):
        echo_exception(self)


class ApiError(click.ClickException):
    """
    API Error (wrong HTTP code)
    """

    def __init__(self, status_code, message):
        click.ClickException.__init__(self, "API return unexpected code: {}. Error: {}".format(status_code, message))
        self.exit_code = ExitCode.API_ERROR.value

    def show(self, file=None):
        echo_exception(self)


class InvalidJsonError(click.ClickException):
    """
    Invalid JSON Error
    """

    def __init__(self, status_code, message):
        click.ClickException.__init__(self, "API return invalid JSON: {}. Error: {}".format(status_code, message))
        self.exit_code = ExitCode.INVALID_JSON_ERROR.value

    def show(self, file=None):
        echo_exception(self)


class NoCredentialsError(click.ClickException):
    """
    Config Error
    """

    def __init__(self):
        click.ClickException.__init__(self, "Error: no credentials found. To set them up, use `gmsaas auth login`.")
        self.exit_code = ExitCode.CONFIGURATION_ERROR.value

    def show(self, file=None):
        echo_exception(self)


class NoAndroidToolsError(click.ClickException):
    """
    Config Error
    """

    def __init__(self):
        click.ClickException.__init__(self, "Error: no Android SDK path set. To set it up, use `gmsaas config`.")
        self.exit_code = ExitCode.CONFIGURATION_ERROR.value

    def show(self, file=None):
        echo_exception(self)


class PackageError(click.ClickException):
    """
    Package Error
    """

    def __init__(self):
        click.ClickException.__init__(self, "Error: `gmsaas` seems corrupted, try to re-install it.")
        self.exit_code = ExitCode.PACKAGE_ERROR.value

    def show(self, file=None):
        echo_exception(self, extra_message="Impossible to use adbtunnel binary within gmsaas package")


class MismatchedVersionError(click.ClickException):
    """
    Mismatched version Error
    """

    def __init__(self, gmsaas_version, adbtunnel_version):
        self.gmsaas_version = gmsaas_version
        self.adbtunnel_version = adbtunnel_version
        click.ClickException.__init__(
            self,
            "Error: incompatible version numbers.\n"
            "gmadbtunneld version is `{}`.\n"
            "gmsaas version is `{}`.\n"
            "Please use same version numbers, or kill `gmadbtunneld`.".format(adbtunnel_version, gmsaas_version),
        )
        self.exit_code = ExitCode.COMPATIBILITY_ERROR.value

    def show(self, file=None):
        echo_exception(self)


class MismatchedPlatformUrlError(click.ClickException):
    """
    Mismatched platform url Error
    """

    def __init__(self, gmsaas_platform_url, adbtunnel_platform_url):
        self.gmsaas_platform_url = gmsaas_platform_url
        self.adbtunnel_platform_url = adbtunnel_platform_url
        click.ClickException.__init__(
            self,
            "Error: inconsistent server URLs.\n"
            "gmadbtunneld connects to `{}`.\n"
            "gmsaas connects to `{}`.\n"
            "Please use same server URLs, or kill `gmadbtunneld`.".format(adbtunnel_platform_url, gmsaas_platform_url),
        )
        self.exit_code = ExitCode.COMPATIBILITY_ERROR.value

    def show(self, file=None):
        echo_exception(self)


class UnreachableError(click.ClickException):
    """
    Unreachable Error
    """

    def __init__(self):
        click.ClickException.__init__(self, "Error: unable to connect to Genymotion SAAS server")
        self.exit_code = ExitCode.UNREACHABLE_ERROR.value

    def show(self, file=None):
        echo_exception(self, extra_message="Unable to setting up SIO")


def _get_instance_error(instance_uuid, expected_state, actual_state):
    assert expected_state in [InstanceState.ONLINE, InstanceState.DELETED], "Expected state is not subject to error"

    if expected_state == InstanceState.ONLINE:
        if is_instance_starting(actual_state):
            return "Error: instance `{}` did not start in time, please check its state with `gmsaas instances list`".format(
                instance_uuid
            )
        elif is_instance_stopping(actual_state):
            return "Error: instance `{}` has been stopped".format(instance_uuid)
        return "Error: instance `{}` failed to start, please check its state with `gmsaas instances list`".format(
            instance_uuid
        )

    if is_instance_stopping(actual_state):
        return "Error: instance `{}` did not stop in time, please check its state with `gmsaas instances list`".format(
            instance_uuid
        )
    return "Error: instance `{}` failed to stop, please check its state with `gmsaas instances list`".format(
        instance_uuid
    )


class InstanceError(click.ClickException):
    """
    Instance Error
    """

    def __init__(self, instance_uuid, expected_state, actual_state):
        click.ClickException.__init__(self, _get_instance_error(instance_uuid, expected_state, actual_state))
        self.instance_uuid = instance_uuid
        self.actual_state = actual_state
        self.expected_state = expected_state
        self.exit_code = ExitCode.INSTANCE_ERROR.value

    def show(self, file=None):
        echo_exception(
            self,
            extra_message="Instance `{}` expects to be `{}` but reached `{}`".format(
                self.instance_uuid, self.expected_state, self.actual_state
            ),
        )


class AdbTunnelBusyPortError(click.ClickException):
    """
    AdbTunnel Busy Port Error
    """

    def __init__(self, instance_uuid, port):
        click.ClickException.__init__(self, "Adb tunnel communication failure. Port {} is not available.".format(port))
        self.instance_uuid = instance_uuid
        self.port = port
        self.exit_code = ExitCode.ADBTUNNEL_BUSY_PORT_ERROR.value

    def show(self, file=None):
        echo_exception(
            self,
            extra_message="Failed to connect instance {} to adbtunnel: port {} is busy".format(
                self.instance_uuid, self.port
            ),
        )


class AdbTunnelGenericError(click.ClickException):
    """
    AdbTunnel Generic Error
    """

    def __init__(self, instance_uuid):
        click.ClickException.__init__(self, "Adb tunnel communication failure.")
        self.instance_uuid = instance_uuid
        self.exit_code = ExitCode.ADBTUNNEL_GENERIC_ERROR.value

    def show(self, file=None):
        echo_exception(self, extra_message="Failed to connect instance {} to adbtunnel".format(self.instance_uuid))


class AdbTunnelRunningOnDifferentPortError(click.ClickException):
    """
    AdbTunnel Running On Different Port
    """

    def __init__(self, instance_uuid, running_port, wanted_port):
        click.ClickException.__init__(self, "Instance already connected to ADB tunnel on port {}.".format(running_port))
        self.instance_uuid = instance_uuid
        self.running_port = running_port
        self.wanted_port = wanted_port
        self.exit_code = ExitCode.ADBTUNNEL_DIFFERENT_PORT_ERROR.value

    def show(self, file=None):
        echo_exception(
            self,
            extra_message="Instance {} cannot connect to adbtunnel with port {}: already connected on port {}".format(
                self.instance_uuid, self.wanted_port, self.running_port
            ),
        )


def _get_adbtunnel_instance_error(instance_uuid, instance_state):
    assert instance_state != InstanceState.ONLINE

    if instance_state == InstanceState.UNKNOWN:
        return "Error: instance `{}` does not exist.".format(instance_uuid)
    return "Error: instance `{}` is not started yet.".format(instance_uuid)


class AdbTunnelInstanceNotReadyError(click.ClickException):
    """
    AdbTunnel Instance Not Ready
    """

    def __init__(self, instance_uuid, instance_state):
        click.ClickException.__init__(self, _get_adbtunnel_instance_error(instance_uuid, instance_state))
        self.instance_uuid = instance_uuid
        self.instance_state = instance_state
        self.exit_code = ExitCode.ADBTUNNEL_INSTANCE_NOT_READY.value

    def show(self, file=None):
        echo_exception(
            self,
            extra_message="Instance {} cannot connect to adbtunnel: state={}".format(
                self.instance_uuid, self.instance_state
            ),
        )


class RequestError(click.ClickException):
    """
    Request Error
    """

    def __init__(self, request_exception):
        click.ClickException.__init__(self, "Error: no network connection")
        self.exception = request_exception
        self.exit_code = ExitCode.REQUEST_ERROR.value

    def show(self, file=None):
        echo_exception(self, extra_message=str(self.exception))


class LogzipError(click.ClickException):
    """
    Logzip Error
    """

    def __init__(self, logzip_exception):
        click.ClickException.__init__(self, "Error: unable to generate logs archive")
        self.exception = logzip_exception
        self.exit_code = ExitCode.LOGZIP_ERROR.value

    def show(self, file=None):
        echo_exception(self, extra_message=str(self.exception))
