#   Copyright 2019 Intel, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

from rsdclient.common import base
from rsdclient.common import utils


class RootManager(base.Manager):
    _resource_name = "root service"

    def __init__(self, *args, **kwargs):
        super(RootManager, self).__init__(*args, **kwargs)

    def get(self, resource_uri):
        resource = self.client.get_resource(resource_uri)
        resource_dict = utils.extract_attr(resource)

        return resource_dict

    def delete(self, resource_uri):
        self.client._conn.delete(resource_uri)

    def patch(self, target_uri, data=None):
        self.client._conn.patch(target_uri, data=data)

    def post(self, target_uri, data=None):
        self.client._conn.post(target_uri, data=data)
