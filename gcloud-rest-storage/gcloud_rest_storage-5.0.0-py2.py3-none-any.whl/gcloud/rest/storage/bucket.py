from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import object
import logging
from typing import List
from typing import Optional

from gcloud.rest.auth import BUILD_GCLOUD_REST  # pylint: disable=no-name-in-module

from .blob import Blob

# Selectively load libraries based on the package
if BUILD_GCLOUD_REST:
    from requests import HTTPError as ResponseError
    from requests import Session
else:
    from aiohttp import ClientResponseError as ResponseError
    from aiohttp import ClientSession as Session

log = logging.getLogger(__name__)


class Bucket(object):
    def __init__(self, storage, name     )        :
        self.storage = storage
        self.name = name

    def get_blob(self, blob_name     ,
                       session                    = None)        :
        metadata = self.storage.download_metadata(self.name, blob_name,
                                                        session=session)

        return Blob(self, blob_name, metadata)

    def blob_exists(self, blob_name     ,
                          session                    = None)        :
        try:
            self.get_blob(blob_name, session=session)
            return True
        except ResponseError as e:
            try:
                if e.status in {404, 410}:
                    return False
            except AttributeError:
                if e.code in {404, 410}:
                    return False

            raise e

    def list_blobs(self, prefix      = '',
                         session                    = None)             :
        params = {'prefix': prefix}
        content = self.storage.list_objects(self.name, params=params,
                                                  session=session)

        return [x['name'] for x in content.get('items', list())]

    def new_blob(self, blob_name     )        :
        return Blob(self, blob_name, {'size': 0})
