import json
import os
import urllib
from os.path import normpath, dirname
from urllib.parse import urlparse

from azure.common import AzureHttpError, AzureMissingResourceHttpError
from azure.storage.blob import BlockBlobService

from azureml.studio.package_info import PROJECT_ROOT_PATH
from azureml.studio.common.error import ErrorMapping, IncorrectAzureStorageOrKeyError, IncorrectAzureBlobNameError, \
    IncorrectAzureContainerError
from azureml.studio.core.logger import common_logger
from azureml.studio.core.utils.fileutils import ensure_folder
from azureml.studio.core.utils.strutils import remove_prefix


class AzureBlobUri:
    _SAS_TOKEN_DELIMITER = "?"
    _URI_DELIMITER = "/"
    _BLOB_HOSTNAME_SUFFIX = ".blob.core.windows.net"

    def __init__(self, blob_uri):
        self.blob_full_uri = blob_uri.strip()

        blob_url = urlparse(self.blob_full_uri)
        if blob_url.query:
            self.sas_token = blob_url.query
        else:
            self.sas_token = ""

        if blob_url.hostname:
            self.account_name = blob_url.hostname.replace(self._BLOB_HOSTNAME_SUFFIX, "")
        else:
            self.account_name = ""

        parts = blob_url.path.strip(self._URI_DELIMITER).split(self._URI_DELIMITER)
        self.container_name = parts[0]
        # Here use the urldecode to decode the relative file path
        # For SAS case, users may just copy the URL from Azure portal, which will encode the space to %20 in file name
        # However, Azure Blob SDK cannot recognize the encoded file name, so need to decode the file path here
        self.blob_path = urllib.parse.unquote_plus(self._URI_DELIMITER.join(parts[1:]))


BLOB_CONNECT_TIMEOUT_SEC = 60


def get_blob_service_by_workspace_name(workspace_name, conf_file=os.path.join(PROJECT_ROOT_PATH, 'credential.json')):
    if not os.path.isfile(conf_file):
        raise FileNotFoundError(f"Config file {conf_file} does not exist")

    with open(conf_file) as f:
        dct = json.load(f)

        connection_strings_dct = dct.get('connection_strings')
        if not connection_strings_dct:
            raise ValueError(f"Config file {conf_file} does not contain information for 'connection_strings'.")
        if not isinstance(connection_strings_dct, dict):
            raise ValueError(f"'connection_strings' in {conf_file} must be a dict type.")

        connection_string = connection_strings_dct.get(workspace_name)
        if not connection_string:
            raise ValueError(f"Unrecognized workspace name: {workspace_name}")
        if not isinstance(connection_string, str):
            raise ValueError(f"Connection string in config file {conf_file} must be a string type.")

    return BlockBlobService(connection_string=connection_string)


class AzureBlobContainer:
    def __init__(self, container_name: str, workspace_name: str = 'demo_workspace'):
        self._container_name = container_name
        self._service = get_blob_service_by_workspace_name(workspace_name)

    def list_blobs(self, prefix=None):
        try:
            return self._service.list_blobs(
                container_name=self._container_name,
                prefix=prefix
            )
        except AzureHttpError as azure_http_error:
            self._handle_azure_error(azure_http_error)

    def download_blob_to_file(self, blob_name, file_name):
        common_logger.info(f"Downloading {blob_name} to {file_name}")
        ensure_folder(dirname(file_name))
        try:
            return self._service.get_blob_to_path(
                container_name=self._container_name,
                blob_name=blob_name,
                file_path=file_name,
                timeout=BLOB_CONNECT_TIMEOUT_SEC
            )
        except AzureHttpError as azure_http_error:
            self._handle_azure_error(azure_http_error)

    def download_blob_to_stream(self, blob_name, stream):
        common_logger.info(f"Downloading {blob_name}")
        try:
            return self._service.get_blob_to_stream(
                container_name=self._container_name,
                blob_name=blob_name,
                stream=stream,
                timeout=BLOB_CONNECT_TIMEOUT_SEC
            )
        except AzureHttpError as azure_http_error:
            self._handle_azure_error(azure_http_error)

    def download_blobs_to_folder(self, prefix, folder):
        not_found = object()

        b = not_found
        for b in self.list_blobs(prefix=prefix):
            relative_path = remove_prefix(b.name, prefix).strip('/')
            # skip for folder itself
            if not relative_path:
                continue

            file_name = os.path.join(folder, normpath(relative_path))
            self.download_blob_to_file(b.name, file_name)

        if b is not_found:
            raise IncorrectAzureBlobNameError(blob_name_prefix=prefix)

    def _handle_azure_error(self, azure_http_error):
        if isinstance(azure_http_error, AzureMissingResourceHttpError):
            ErrorMapping.rethrow(azure_http_error, IncorrectAzureContainerError(container_name=self._container_name))
        elif azure_http_error.status_code == 403:
            ErrorMapping.rethrow(azure_http_error, IncorrectAzureStorageOrKeyError())
        else:
            # TODO: add a ModuleError here
            raise azure_http_error
