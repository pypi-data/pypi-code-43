from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import json
import uuid

import pytest
from gcloud.rest.auth import BUILD_GCLOUD_REST  # pylint: disable=no-name-in-module
from gcloud.rest.storage import Storage

# Selectively load libraries based on the package
if BUILD_GCLOUD_REST:
    from requests import HTTPError as ResponseError
    from requests import Session
else:
    from aiohttp import ClientResponseError as ResponseError
    from aiohttp import ClientSession as Session


#@pytest.mark.asyncio
@pytest.mark.parametrize('uploaded_data,expected_data,file_extension', [
    ('test', b'test', 'txt'),
    (b'test', b'test', 'bin'),
    (json.dumps({'data': 1}), json.dumps({'data': 1}).encode('utf-8'), 'json'),
])
def test_object_life_cycle(bucket_name, creds, uploaded_data,
                                 expected_data, file_extension):
    object_name = '{}/{}.{}'.format((uuid.uuid4().hex), (uuid.uuid4().hex), (file_extension))

    with Session() as session:
        storage = Storage(service_file=creds, session=session)
        storage.upload(bucket_name, object_name, uploaded_data)

        bucket = storage.get_bucket(bucket_name)
        blob = bucket.get_blob(object_name)
        constructed_result = blob.download()
        assert constructed_result == expected_data

        direct_result = storage.download(bucket_name, object_name)
        assert direct_result == expected_data

        storage.delete(bucket_name, object_name)

        with pytest.raises(ResponseError):
            storage.download(bucket_name, object_name)
