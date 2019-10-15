from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import str
from future import standard_library
standard_library.install_aliases()
from builtins import object
import io
import uuid
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from gcloud.rest.auth import SyncSession  # pylint: disable=no-name-in-module
from gcloud.rest.auth import BUILD_GCLOUD_REST  # pylint: disable=no-name-in-module
from gcloud.rest.auth import Token  # pylint: disable=no-name-in-module

try:
    import ujson as json
except ImportError:
    import json  # type: ignore

# Selectively load libraries based on the package
if BUILD_GCLOUD_REST:
    from requests import Session
else:
    from aiohttp import ClientSession as Session

API_ROOT = 'https://www.googleapis.com/bigquery/v2'
SCOPES = [
    'https://www.googleapis.com/auth/bigquery.insertdata',
]


class Table(object):
    def __init__(self, dataset_name     , table_name     ,
                 project                = None,
                 service_file                                  = None,
                 session                    = None,
                 token                  = None)        :
        self._project = project
        self.dataset_name = dataset_name
        self.table_name = table_name

        self.session = SyncSession(session)
        self.token = token or Token(service_file=service_file, scopes=SCOPES,
                                    session=self.session.session)

    def project(self)       :
        if self._project:
            return self._project

        self._project = self.token.get_project()
        if self._project:
            return self._project

        raise Exception('could not determine project, please set it manually')

    @staticmethod
    def _make_insert_body(rows                      ,
                          skip_invalid       = False,
                          ignore_unknown       = True)                  :
        return {
            'kind': 'bigquery#tableDataInsertAllRequest',
            'skipInvalidRows': skip_invalid,
            'ignoreUnknownValues': ignore_unknown,
            'rows': [{
                'insertId': uuid.uuid4().hex,
                'json': row
            } for row in rows],
        }

    def headers(self)                  :
        token = self.token.get()
        return {
            'Authorization': 'Bearer {}'.format((token)),
        }

    def insert(self, rows                      ,
                     skip_invalid       = False, ignore_unknown       = True,
                     session                    = None,
                     timeout      = 60)                  :
        """
        Streams data into BigQuery

        The response payload will include an `insertErrors` key if a subset of
        the rows failed to get inserted.
        """
        if not rows:
            return {}

        project = self.project()
        url = ('{}/projects/{}/datasets/{}/'
               'tables/{}/insertAll'.format((API_ROOT), (project), (self.dataset_name), (self.table_name)))

        body = self._make_insert_body(rows, skip_invalid=skip_invalid,
                                      ignore_unknown=ignore_unknown)
        payload = json.dumps(body).encode('utf-8')

        headers = self.headers()
        headers.update({
            'Content-Length': str(len(payload)),
            'Content-Type': 'application/json'
        })

        s = SyncSession(session) if session else self.session
        resp = s.post(url, data=payload, headers=headers, params=None,
                            timeout=timeout)
        return resp.json()
