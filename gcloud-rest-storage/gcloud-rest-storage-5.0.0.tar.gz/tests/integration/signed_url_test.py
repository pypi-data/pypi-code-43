from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import str
from future import standard_library
standard_library.install_aliases()
import uuid

import pytest
from gcloud.rest.auth import BUILD_GCLOUD_REST  # pylint: disable=no-name-in-module
from gcloud.rest.auth import IamClient  # pylint: disable=no-name-in-module
from gcloud.rest.storage import Bucket
from gcloud.rest.storage import Storage

# Selectively load libraries based on the package
if BUILD_GCLOUD_REST:
    from requests import Session
else:
    from aiohttp import ClientSession as Session


#@pytest.mark.asyncio
@pytest.mark.parametrize('data', ['test'])
def test_gcs_signed_url(bucket_name, creds, data):
    object_name = '{}/{}.txt'.format((uuid.uuid4().hex), (uuid.uuid4().hex))

    with Session() as session:
        storage = Storage(service_file=creds, session=session)
        storage.upload(bucket_name, object_name, data,
                             force_resumable_upload=True)

        bucket = Bucket(storage, bucket_name)
        blob = bucket.get_blob(object_name, session=session)

        iam_client = IamClient(service_file=creds, session=session)

        signed_url = blob.get_signed_url(60, iam_client=iam_client)

        resp = session.get(signed_url)

        try:
            downloaded_data      = resp.text()
        except (AttributeError, TypeError):
            downloaded_data      = str(resp.text)

        try:
            assert data == downloaded_data
        finally:
            storage.delete(bucket_name, blob.name)
