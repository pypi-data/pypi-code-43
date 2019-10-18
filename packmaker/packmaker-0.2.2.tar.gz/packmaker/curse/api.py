# vim:set ts=4 sw=4 et nowrap syntax=python ff=unix:
#
# Copyright 2019 Mark Crewson <mark@crewson.net>
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

import requests

from ..framew.baseobject import BaseObject

##############################################################################


class CurseAPI (BaseObject):

    max_pagesize = 1000
    max_index = 10000

    def __init__(self):
        super(BaseObject, self).__init__()

    def _api_baseurl(self):
        raise NotImplementedError

    def _request_headers(self):
        return None

    def _getrequest(self, url, params=None):
        r = requests.get(self._api_baseurl() + url, params, timeout=60, headers=self._request_headers())
        r.raise_for_status()
        return r

    def _postrequest(self, url, data):
        r = requests.post(self._api_baseurl() + url, json=data, timeout=60, headers=self._request_headers())
        r.raise_for_status()
        return r

    def get_addon(self, projectId):
        return self._getrequest('addon/{}'.format(projectId)).json()

    def get_addons(self, projectIds):
        return self._postrequest('addon', projectIds).json()

    def get_addon_files(self, projectId):
        return self._getrequest('addon/{}/files'.format(projectId)).json()

    def get_addons_by_criteria(self,
                               gameId,
                               sectionId=None,
                               categoryIds=None,
                               sort='Featured',
                               sortDescending=True,
                               gameVersions=None,
                               index=0,
                               pageSize=1000,
                               searchFilter=None):
        url = 'addon/search'
        parameters = {"gameID": gameId,
                      "sort": sort,
                      "sortDescending": sortDescending,
                      "index": index,
                      "pageSize": pageSize
                      }

        if sectionId is not None:
            parameters['sectionId'] = sectionId
        if categoryIds is not None:
            parameters['categoryId'] = categoryIds
        if gameVersions is not None:
            parameters['gameVersion'] = gameVersions
        if searchFilter is not None:
            parameters['searchFilter'] = searchFilter

        return self._getrequest(url, parameters).json()

    def yield_addons_by_criteria(self,
                                 gameId,
                                 sectionId=None,
                                 categoryIds=None,
                                 sort='Featured',
                                 sortDescending=True,
                                 gameVersions=None,
                                 pageSize=1000,
                                 searchFilter=None):

        if pageSize > self.max_pagesize:
            raise 'curse api limits pagesize to 1000'

        index = 0
        done = False
        while not done:
            results = self.get_addons_by_criteria(gameId, sectionId, categoryIds,
                                                  sort, sortDescending, gameVersions,
                                                  index, pageSize, searchFilter)
            index += pageSize
            if len(results) < pageSize:
                done = True

            if index > self.max_index:
                done = True
            else:
                if index + pageSize > self.max_index:
                    pageSize = self.max_index - index
                    if pageSize < 1:
                        done = True

            for addon in results:
                yield addon

##############################################################################
# THE END
