import json
from urllib.parse import urljoin

import requests


class PtyDevopsAPI:
    def __init__(self, url: str, version: str = "v1"):
        """Class constructor

        :param url: api endpoint url, ex: http://example.com:25100
        :param version: api version, default: "v1")
        """
        self.url = url
        self.version = version
        self.api_url = urljoin(url, "api/{}/".format(version))
        self.req_header = {"Content-Type": "application/json"}

    def get_version(self):
        """Get the API version"""
        return self.__get("version")

    def get_health(self):
        """Get PIM cluster health"""
        return self.__get("health")

    def get_log_level(self):
        """Get the log level"""
        return self.__get("log")

    def set_log_level(self, level: str):
        """Set the log level

        :param level: log level
        """
        data = {"level": level}
        return self.__post("log", data)

    def init(self, mongo_host: str):
        """Bootstrap the PIM cluster
        
        :param mongo_host: mongo hostname required at initialization
        """
        data = {"mongoHost": mongo_host}
        return self.__post("init", data)

    def list_datastores(self):
        """List all datastores"""
        return self.__get("datastores")

    def create_datastore(self, name: str, description: str, default: bool):
        """Create a datastore

        :param name: datastore name
        :param description: datastore description
        :param default: whether or not datastore should be default
        """
        data = {"name": name, "description": description, "default": default}

        return self.__post("datastores", data)

    def get_datastore(self, datastore_uid: str):
        """Get a specific data store

        :param datastore_uid: datastore unique id
        """
        return self.__get("datastores/{}", datastore_uid)

    def delete_datastore(self, datastore_uid: str):
        """Delete a specific data store

        :param datastore_uid: datastore unique id
        """
        return self.__delete("datastores/{}", datastore_uid)

    def list_datastore_ranges(self, datastore_uid: str):
        """List ranges for a specific data store

        :param datastore_uid: datastore unique id
        """
        return self.__get("datastores/{}/ranges", datastore_uid)

    def create_datastore_range(
        self, datastore_uid: str, range_from: str, range_to: str
    ):
        """Create a range for a specific data store

        :param datastore_uid: datastore unique id
        :param range_from: example: 192.168.1.1
        :param range_to: example: 192.168.1.2
        """
        params = {"dataStoreUid": datastore_uid}
        data = {"from": range_from, "to": range_to}
        return self.__post(
            "datastores/{}/ranges", data, datastore_uid, params
        )

    def get_datastore_range(self, datastore_uid: str, range_uid: str):
        """Get a specific range from a specific data store

        :param datastore_uid: datastore unique id
        :param range_uid: range unique id
        """
        return self.__get(
            "datastores/{}/ranges/{}", datastore_uid, range_uid
        )

    def delete_datastore_range(self, datastore_uid: str, range_uid: str):
        """Delete a specific range from a specific data store

        :param datastore_uid: datastore unique id
        :param range_uid: range unique id
        """
        return self.__delete(
            "datastores/{}/ranges/{}", datastore_uid, range_uid
        )

    def list_masks(self):
        """List all masks"""
        return self.__get("masks")

    def create_mask(
        self,
        name: str,
        description: str,
        from_left: int,
        from_right: int,
        masked: bool,
        character: str,
    ):
        """Create a mask

        :param name: mask name
        :param description: mask description
        :param from_left: position from left
        :param from_right: position from right
        :param masked: whether or not to use mask
        :param character: mask character
        """
        data = {
            "name": name,
            "description": description,
            "fromLeft": from_left,
            "fromRight": from_right,
            "masked": masked,
            "character": character,
        }
        return self.__post("masks", data)

    def get_mask(self, mask_uid: str):
        """Get a specific mask

        :param mask_uid: mask unique id
        """
        return self.__get("masks/{}", mask_uid)

    def delete_mask(self, mask_uid: str):
        """Delete a specific mask

        :param mask_uid: mask unique id
        """
        return self.__delete("masks/{}", mask_uid)

    def list_data_elements(self):
        """List all data elements"""
        return self.__get("dataelements")

    def create_data_element(self, data_element_properties: dict):
        """Create a data element

        :param data_element_properties: data element design, see schema for example
        """
        return self.__post("dataelements", data_element_properties)

    def get_data_element(self, data_element_uid: str):
        """Get a specific data element

        :param data_element_uid: data element unique id
        """
        return self.__get("dataelements/{}", data_element_uid)

    def delete_data_element(self, data_element_uid: str):
        """Delete a specific data element

        :param data_element_uid: data element unique id
        """
        return self.__delete("dataelements/{}", data_element_uid)

    def list_applications(self):
        """List all applications"""
        return self.__get("applications")

    def create_application(
        self,
        name: str,
        description: str,
        application_name: str,
        application_user: str,
        audit_success: bool,
    ):
        """Create an application

        :param name: application name
        :param description: application description
        :param application_name: real application name
        :param application_user: application user
        :param audit_success: whether or not audit is used
        """
        data = {
            "name": name,
            "description": description,
            "applicationName": application_name,
            "applicationUser": application_user,
            "auditSuccess": audit_success,
        }
        return self.__post("applications", data)

    def get_application(self, application_uid: str):
        """Get a specific application

        :param application_uid: application unique id
        """
        return self.__get("applications/{}", application_uid)

    def delete_application(self, application_uid: str):
        """Delete a specific application

        :param application_uid: application unique id
        """
        return self.__delete("applications/{}", application_uid)

    def list_policies(self):
        """List all policies"""
        return self.__get("policies")

    def create_policy(self, policy_properties: dict):
        """Create a policy

        :param policy_properties: policy design, see schema for example
        """
        return self.__post("policies", policy_properties)

    def get_policy(self, policy_uid: str):
        """Get a specific policy

        :param policy_uid: policy unique id
        """
        return self.__get("policies/{}", policy_uid)

    def delete_policy(self, policy_uid: str):
        """Delete a specific policy

        :param policy_uid: policy unique id
        """
        return self.__delete("policies/{}", policy_uid)

    def list_policy_rules(self, policy_uid: str):
        """List all rules for a specific policy

        :param policy_uid: policy unique id
        """
        return self.__get("policies/{}/rules", policy_uid)

    def create_rule(self, policy_uid: str, rule_properties: dict):
        """Create a rule

        :param policy_uid: policy unique id
        :param rule_properties: rule design, see schema for example
        """
        return self.__post("policies/{}/rules", rule_properties, policy_uid)

    def delete_rule(self, policy_uid: str, role_uid: str, data_element_uid: str):
        """Delete a specific rule

        :param policy_uid: policy unique id
        :param role_uid: role unique id
        :param data_element_uid: data element unique id
        """
        return self.__delete(
            "policies/{}/rules/{}/{}",
            policy_uid,
            role_uid,
            data_element_uid,
        )

    def list_sources(self):
        """List all sources"""
        return self.__get("sources")

    def create_source(self, source_properties: dict):
        """Create a source

        :param source_properties: source design, see schema for example
        """
        return self.__post("sources", source_properties)

    def get_source(self, source_uid: str):
        """Get a specific source

        :param source_uid: source unique id
        """
        return self.__get("sources/{}", source_uid)

    def delete_source(self, source_uid: str):
        """Delete a specific source

        :param source_uid: source unique id
        """
        return self.__delete("sources/{}", source_uid)

    def list_source_members(self, source_uid: str):
        """List all members for a specific source

        :param source_uid: source unique id
        """
        return self.__get("sources/{}/members", source_uid)

    def test_source(self, source_uid: str):
        """Test the source connection

        :param source_uid: source unique id
        """
        return self.__get("sources/{}/test", source_uid)

    def list_roles(self):
        """List all roles"""
        return self.__get("roles")

    def create_role(self, name: str, description: str, mode: str, allow_all: bool):
        """Create a role

        :param name: role name
        :param description: role description
        :param mode: update mode
        :param allow_all: whether or not to allow access to all users
        """
        data = {
            "name": name,
            "description": description,
            "mode": mode,
            "allowAll": allow_all,
        }
        return self.__post("roles", data)

    def get_role(self, role_uid: str):
        """Get a specific role

        :param role_uid: role unique id
        """
        return self.__get("roles/{}", role_uid)

    def delete_role(self, role_uid: str):
        """Delete a specific role

        :param role_uid: role unique id
        """
        return self.__delete("roles/{}", role_uid)

    def list_role_members(self, role_uid: str):
        """List all members for a specific role

        :param role_uid: role unique id
        """
        return self.__get("roles/{}/members", role_uid)

    def add_role_member(self, role_uid: str, role_members: list):
        """Add member(s) to a role

        :param role_uid: role unique id
        :param role_members: role members, see schema for example
        """
        params = {"roleUid": role_uid}
        data = role_members
        return self.__post(
            "roles/{}/members", data, role_uid, params
        )

    def get_role_member(self, role_uid: str, member_uid: str):
        """Get a specific role member

        :param role_uid: role unique id
        :param member_uid: member unique id
        """
        return self.__get(
            "roles/{}/members/{}", role_uid, member_uid
        )

    def delete_role_member(self, role_uid: str, member_uid: str):
        """Delete a specific role member

        :param role_uid: role unique id
        :param member_uid: member unique id
        """
        return self.__delete(
            "roles/{}/members/{}", role_uid, member_uid
        )

    def list_role_member_users(self, role_uid: str, member_uid: str):
        """List all users for a specific role member

        :param role_uid: role unique id
        :param member_uid: member unique id
        """
        return self.__get(
            "roles/{}/members/{}/users", role_uid, member_uid
        )

    def role_sync(self, role_uid: str):
        """Sync roles

        :param role_uid: role unique id
        """
        data = {}
        return self.__post("roles/{}/sync", data, role_uid)

    def deploy(self, deploy_properties: dict):
        """Deploy

        :param deploy_properties: deploy design, see schema for example
        """
        return self.__post("deploy", deploy_properties)

    def __delete(self, resource: str, *args) -> requests.Response:
        """Make a delete request, all subsequent args will be formatted to api url

        :param resource: api resource url
        """
        response = requests.delete(urljoin(self.api_url, resource.format(*args)))
        return response

    def __get(self, resource: str, *args) -> requests.Response:
        """Make a get request, all subsequent args will be formatted to api url

        :param resource: api resource url
        """
        response = requests.get(urljoin(self.api_url, resource.format(*args)))
        return response

    def __post(
        self, resource: str, data: dict, *args, params=None
    ) -> requests.Response:
        """Make a post request, all subsequent args will be formatted to api url

        :param resource: api resource url
        :param data: request json body
        :param params optional: request parameters
        """
        response = requests.post(
            urljoin(self.api_url, resource.format(*args)),
            json=data,
            headers=self.req_header,
            params=params,
        )
        return response
