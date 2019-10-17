# Copyright 2019 Genymobile
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
"""
Genymotion Cloud SaaS API constants
"""

import os

CLOUD_BASE_URL = os.environ.get("GM_PLATFORM_BASE_URL", "https://api.geny.io/cloud")
LOGIN_URL = "{}/v1/users/login".format(CLOUD_BASE_URL)
RECIPES_URL = "{}/v1/recipes".format(CLOUD_BASE_URL)
INSTANCES_URL = "{}/v1/instances".format(CLOUD_BASE_URL)


def get_start_disposable_url(recipe_uuid):
    """
    Return final url to start an instance
    """
    return "{}/{}/start-disposable".format(RECIPES_URL, recipe_uuid)


def get_stop_disposable_url(instance_uuid):
    """
    Return final url to stop an instance
    """
    return "{}/{}/stop-disposable".format(INSTANCES_URL, instance_uuid)


def get_instance_details_url(instance_uuid):
    """
    Return final url to get details of one instance
    """
    return "{}/{}".format(INSTANCES_URL, instance_uuid)
