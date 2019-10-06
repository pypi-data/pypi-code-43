# Copyright 2019 Zadara Storage, Inc.
# Originally authored by Jeremy Brown - https://github.com/jwbrown77
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy
# of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations
# under the License.


def get_all_storage_policies(session, return_type=None):
    path = '/api/zios/policies.json'
    return session.get_api(path=path, return_type=return_type)


def get_storage_policy(session, policy_id, return_type=None):
    path = '/api/zios/policies/{0}.json'.format(policy_id)
    return session.get_api(path=path, return_type=return_type)


def update_storage_policy(session, policy_id, full_description, gb_per_month_cost, return_type=None):
    path = '/api/zios/policies/{0}.json'.format(policy_id)
    body_values = {'full_description': full_description, 'gb_per_month_cost': gb_per_month_cost}
    return session.put_api(path=path, body=body_values, return_type=return_type)


def set_default_storage_policy(session, policy_id, full_description, gb_per_month_cost, return_type=None):
    path = '/api/zios/policies/{0}/set_default.json'.format(policy_id)
    body_values = {'full_description': full_description, 'gb_per_month_cost': gb_per_month_cost}
    return session.post_api(path=path, body=body_values, return_type=return_type)
