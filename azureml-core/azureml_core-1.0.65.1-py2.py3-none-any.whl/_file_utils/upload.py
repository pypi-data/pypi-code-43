# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from azureml._restclient.clientbase import execute_func_with_reset
from six.moves.urllib import parse

module_logger = logging.getLogger(__name__)


def get_block_blob_service_credentials(sas_url):
    parsed_url = parse.urlparse(sas_url)

    sas_token = parsed_url.query

    account_name = parsed_url.netloc.split(".", 2)[0]

    path = parsed_url.path
    # Remove leading / to avoid awkward parse
    if path[0] == "/":
        path = path[1:]
    container_name, blob_name = path.split("/", 1)

    return sas_token, account_name, container_name, blob_name


def upload_blob_from_stream(stream, url, content_type=None, session=None, timeout=None, backoff=None, retries=None):
    # TODO add support for upload without azure.storage
    from azureml._vendor.azure_storage.blob import BlockBlobService
    from azureml._vendor.azure_storage.blob.models import ContentSettings
    sas_token, account_name, container_name, blob_name = get_block_blob_service_credentials(url)
    content_settings = ContentSettings(content_type=content_type)
    blob_service = BlockBlobService(account_name=account_name, sas_token=sas_token, request_session=session)
    reset_func = StreamResetFunction(stream.tell())
    return execute_func_with_reset(backoff,
                                   retries,
                                   blob_service.create_blob_from_stream,
                                   reset_func,
                                   container_name=container_name,
                                   blob_name=blob_name,
                                   stream=stream,
                                   content_settings=content_settings,
                                   timeout=timeout)


class StreamResetFunction():
    def __init__(self, position):
        self.position = position

    def __call__(self, stream, *args, **kwargs):
        stream.seek(self.position)
