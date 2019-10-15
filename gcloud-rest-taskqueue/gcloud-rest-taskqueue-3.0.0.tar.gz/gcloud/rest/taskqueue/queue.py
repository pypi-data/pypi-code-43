"""
An asynchronous push queue for Google Appengine Task Queues
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import object
import io
import logging
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

import backoff
from gcloud.rest.auth import SyncSession  # pylint: disable=no-name-in-module
from gcloud.rest.auth import BUILD_GCLOUD_REST  # pylint: disable=no-name-in-module
from gcloud.rest.auth import Token  # pylint: disable=no-name-in-module

# Selectively load libraries based on the package
if BUILD_GCLOUD_REST:
    from requests import Session
else:
    from aiohttp import ClientSession as Session

API_ROOT = 'https://cloudtasks.googleapis.com'
LOCATION = 'us-central1'
SCOPES = [
    'https://www.googleapis.com/auth/cloud-tasks',
]

log = logging.getLogger(__name__)


class PushQueue(object):
    def __init__(self, project     , taskqueue     ,
                 service_file                                  = None,
                 location      = LOCATION,
                 session                    = None,
                 token                  = None)        :
        self.base_api_root = '{}/v2beta3'.format((API_ROOT))
        self.api_root = ('{}/projects/{}/'
                         'locations/{}/queues/{}'.format((self.base_api_root), (project), (location), (taskqueue)))
        self.session = SyncSession(session)
        self.token = token or Token(service_file=service_file, scopes=SCOPES,
                                    session=self.session.session)

    def headers(self)                  :
        token = self.token.get()
        return {
            'Authorization': 'Bearer {}'.format((token)),
            'Content-Type': 'application/json',
        }

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)  # type: ignore
    def _request(self, method     , url     ,
                       session                    = None,
                       **kwargs     )       :
        s = SyncSession(session) if session else self.session
        headers = self.headers()

        resp = s.request(method, url, headers=headers,
                               auto_raise_for_status=False, **kwargs)
        # N.B. This is awaited early to give an extra helping hand to various
        # debug tools, which tend to be able to capture assigned variables but
        # not un-awaited data.
        data = resp.json()
        resp.raise_for_status()

        return data

    # https://cloud.google.com/tasks/docs/reference/rest/v2beta3/projects.locations.queues.tasks/create
    def create(self, task                ,
                     session                    = None)       :
        url = '{}/tasks'.format((self.api_root))
        body = {
            'task': task,
            'responseView': 'FULL',
        }

        return self._request('POST', url, json=body, session=session)

    # https://cloud.google.com/tasks/docs/reference/rest/v2beta3/projects.locations.queues.tasks/delete
    def delete(self, tname     ,
                     session                    = None)       :
        url = '{}/{}'.format((self.base_api_root), (tname))

        return self._request('DELETE', url, session=session)

    # https://cloud.google.com/tasks/docs/reference/rest/v2beta3/projects.locations.queues.tasks/get
    def get(self, tname     , full       = False,
                  session                    = None)       :
        url = '{}/{}'.format((self.base_api_root), (tname))
        params = {
            'responseView': 'FULL' if full else 'BASIC',
        }

        return self._request('GET', url, params=params, session=session)

    # https://cloud.google.com/tasks/docs/reference/rest/v2beta3/projects.locations.queues.tasks/list
    def list(self, full       = False, page_size      = 1000,
                   page_token      = '',
                   session                    = None)       :
        url = '{}/tasks'.format((self.api_root))
        params = {
            'responseView': 'FULL' if full else 'BASIC',
            'pageSize': page_size,
            'pageToken': page_token,
        }

        return self._request('GET', url, params=params, session=session)

    # https://cloud.google.com/tasks/docs/reference/rest/v2beta3/projects.locations.queues.tasks/run
    def run(self, tname     , full       = False,
                  session                    = None)       :
        url = '{}/{}:run'.format((self.base_api_root), (tname))
        body = {
            'responseView': 'FULL' if full else 'BASIC',
        }

        return self._request('POST', url, json=body, session=session)
