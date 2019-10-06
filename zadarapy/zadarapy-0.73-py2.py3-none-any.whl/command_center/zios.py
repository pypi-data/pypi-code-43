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


def get_all_zios_objects(session, cloud_name, return_type=None):
    path = "/api/clouds/{0}/zioses.json".format(cloud_name)
    return session.get_api(path=path, return_type=return_type)


def get_zios_drives(session, cloud_name, zios_id, return_type=None):
    path = "/api/clouds/{0}/zioses/{1}/drives.json".format(cloud_name, zios_id)
    return session.get_api(path=path, return_type=return_type)


def get_zios_virtual_controllers(session, cloud_name, zios_id, return_type=None):
    path = "/api/clouds/{0}/zioses/{1}/virtual_controllers.json".format(cloud_name, zios_id)
    return session.get_api(path=path, return_type=return_type)


def get_zios_stoarge_policies(session, cloud_name, zios_id, return_type=None):
    path = "/api/clouds/{0}/zioses/{1}/storage_policies.json".format(cloud_name, zios_id)
    return session.get_api(path=path, return_type=return_type)


def get_zios_accounts(session, cloud_name, zios_id, return_type=None):
    path = "/api/clouds/{0}/zioses/{1}/accounts.json".format(cloud_name, zios_id)
    return session.get_api(path=path, return_type=return_type)


def get_zios_comments(session, cloud_name, zios_id, return_type=None):
    path = "/api/clouds/{0}/zioses/{1}/comments.json".format(cloud_name, zios_id)
    return session.get_api(path=path, return_type=return_type)


def assign_public_ip(session, cloud_name, zios_id, return_type=None):
    path = "/api/clouds/{0}/zioses/{1}/public_ip/assign.json".format(cloud_name, zios_id)
    return session.post_api(path=path, return_type=return_type)


def unassign_public_ip(session, cloud_name, zios_id, return_type=None):
    path = "/api/clouds/{0}/zioses/{1}/public_ip/unassign.json".format(cloud_name, zios_id)
    return session.post_api(path=path, return_type=return_type)


def upgrade_zios(session, cloud_name, zios_id, return_type=None):
    path = "/api/clouds/{0}/zioses/{1}/public_ip/upgrade.json".format(cloud_name, zios_id)
    return session.post_api(path=path, return_type=return_type)


def hibernate_zios(session, cloud_name, zios_id, return_type=None):
    path = "/api/clouds/{0}/zioses/{1}/public_ip/hibernate.json".format(cloud_name, zios_id)
    return session.post_api(path=path, return_type=return_type)


def restore_zios(session, cloud_name, zios_id, return_type=None):
    path = "/api/clouds/{0}/zioses/{1}/public_ip/restore.json".format(cloud_name, zios_id)
    return session.post_api(path=path, return_type=return_type)


def create_zios_zsnap(session, cloud_name, zios_id, return_type=None):
    path = "/api/clouds/{0}/zioses/{1}/public_ip/zsnap.json".format(cloud_name, zios_id)
    return session.post_api(path=path, return_type=return_type)


def add_drives_to_zios(session, cloud_name, zios_id, drive_type, quantity, policy_id, return_type=None):
    body_values = {'drive_type': drive_type, 'quantity': quantity, 'policy_id': policy_id}
    path = "/api/clouds/{0}/zioses/{1}/public_ip/drives.json".format(cloud_name, zios_id)
    return session.post_api(path=path, body=body_values, return_type=return_type)
