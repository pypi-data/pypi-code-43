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
GMSaaS early checks
"""

import gmsaas
from gmsaas.storage import get_config_storage, get_auth_storage
from gmsaas.saas.authcache import AUTH_EMAIL_KEY, AUTH_PASSWORD_KEY
from gmsaas.saas.api import CLOUD_BASE_URL
from gmsaas.cli.config import SDK_PATH_KEY
from gmsaas.errors import (
    NoCredentialsError,
    NoAndroidToolsError,
    PackageError,
    MismatchedVersionError,
    MismatchedPlatformUrlError,
)
from gmsaas.adbtunnel import get_adb_tunnel


def credentials_required(func):
    """
    Check if credentials are stored locally
    """

    def wrapper(self, *args, **kwargs):
        # pylint: disable=missing-docstring
        if not get_auth_storage().get(AUTH_EMAIL_KEY) or not get_auth_storage().get(AUTH_PASSWORD_KEY):
            raise NoCredentialsError()
        func(self, *args, **kwargs)

    return wrapper


def _get_major_minor(major_minor_patch_version):
    return ".".join(major_minor_patch_version.split(".")[:2])


def adb_tools_required(func):
    """
    Check if android sdk path is stored locally
    and adbtunnel is usable
    """

    def wrapper(self, *args, **kwargs):
        # pylint: disable=missing-docstring
        storage = get_config_storage()
        if not storage.get(SDK_PATH_KEY):
            raise NoAndroidToolsError()
        adbtunnel = get_adb_tunnel()
        if not adbtunnel.is_ready():
            raise PackageError()
        daemon_info = adbtunnel.get_daemon_info()
        if _get_major_minor(gmsaas.__version__) != _get_major_minor(daemon_info.version):
            raise MismatchedVersionError(gmsaas.__version__, daemon_info.version)
        if CLOUD_BASE_URL != daemon_info.platform_url:
            raise MismatchedPlatformUrlError(CLOUD_BASE_URL, daemon_info.platform_url)
        func(self, *args, **kwargs)

    return wrapper
