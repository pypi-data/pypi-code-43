from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import range
from future import standard_library
standard_library.install_aliases()
import uuid

import pytest
from gcloud.rest.auth import BUILD_GCLOUD_REST  # pylint: disable=no-name-in-module
from gcloud.rest.bigquery import Table

# Selectively load libraries based on the package
if BUILD_GCLOUD_REST:
    from requests import Session
else:
    from aiohttp import ClientSession as Session

#@pytest.mark.asyncio  # type: ignore
def test_data_is_inserted(creds     , dataset     , project     ,
                                table     )        :
    rows = [{'key': uuid.uuid4().hex, 'value': uuid.uuid4().hex}
            for i in range(3)]

    with Session() as s:
        t = Table(dataset, table, project=project, service_file=creds,
                  session=s)
        t.insert(rows)
