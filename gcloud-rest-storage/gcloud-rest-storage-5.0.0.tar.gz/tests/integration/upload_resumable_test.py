from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import range
from future import standard_library
standard_library.install_aliases()
import io
import json
import os
import random
import string
import uuid

import pytest
from gcloud.rest.auth import BUILD_GCLOUD_REST  # pylint: disable=no-name-in-module
from gcloud.rest.storage import Storage

# Selectively load libraries based on the package
if BUILD_GCLOUD_REST:
    from requests import Session
else:
    from aiohttp import ClientSession as Session

# TODO: use hypothesis
RANDOM_BINARY = os.urandom(2045)

# Updated statement to make it compatible with python2
rand_str_list = [random.choice(string.ascii_letters) for r in range(0, 1054)]
RANDOM_STRING = ''.join(rand_str_list)


#@pytest.mark.asyncio
@pytest.mark.parametrize('uploaded_data,expected_data,file_extension', [
    ('test', b'test', 'txt'),
    (json.dumps({'data': 1}), json.dumps({'data': 1}).encode('utf-8'), 'json'),
    (json.dumps([1, 2, 3]), json.dumps([1, 2, 3]).encode('utf-8'), 'json'),
    ('test'.encode('utf-8'), 'test'.encode('utf-8'), 'bin'),
    (io.BytesIO(RANDOM_BINARY), RANDOM_BINARY, 'bin'),
    (io.StringIO(RANDOM_STRING), RANDOM_STRING.encode('utf-8'), 'txt'),
])
def test_upload_resumable(bucket_name, creds, uploaded_data,
                                expected_data, file_extension):
    object_name = '{}/{}.{}'.format((uuid.uuid4().hex), (uuid.uuid4().hex), (file_extension))

    with Session() as session:
        storage = Storage(service_file=creds, session=session)
        res = storage.upload(bucket_name, object_name, uploaded_data,
                                   force_resumable_upload=True)

        downloaded_data = storage.download(bucket_name, res['name'])
        assert expected_data == downloaded_data

        storage.delete(bucket_name, res['name'])
