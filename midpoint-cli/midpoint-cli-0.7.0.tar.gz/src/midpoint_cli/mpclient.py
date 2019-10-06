import re
import time
from argparse import Namespace
from collections import OrderedDict
from typing import List, Optional, Tuple
from urllib.parse import urljoin
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from midpoint_cli.patch import patch_from_file

namespaces = {
    'c': 'http://midpoint.evolveum.com/xml/ns/public/common/common-3',
}

endpoints = {
    "ConnectorType": "connectors",
    "ConnectorHostType": "connectorHosts",
    "GenericObjectType": "genericObjects",
    "ResourceType": "resources",
    "UserType": "users",
    "ObjectTemplateType": "objectTemplates",
    "SystemConfigurationType": "systemConfigurations",
    "TaskType": "tasks",
    "ShadowType": "shadows",
    "RoleType": "roles",
    "ValuePolicyType": "valuePolicies",
    "OrgType": "orgs",
    "FunctionLibraryType": "functionLibraries"
}


def optional_text(node: ElementTree):
    return node.text if node is not None else None


class MidpointObject(OrderedDict):
    def get_oid(self) -> Optional[str]:
        return self['OID']

    def get_name(self) -> Optional[str]:
        return self['Name']


class MidpointObjectList(List[MidpointObject]):

    def find_object(self, search_reference) -> Optional[MidpointObject]:
        for mp_obj in self:
            if search_reference in [mp_obj.get_oid(), mp_obj.get_name()]:
                return mp_obj

        return None


class MidpointTask(MidpointObject):

    def __init__(self, xml_entity: Element):
        super().__init__()
        self['OID'] = xml_entity.attrib['oid']
        self['Name'] = xml_entity.find('c:name', namespaces).text
        self['Execution Status'] = xml_entity.find('c:executionStatus', namespaces).text
        rs = xml_entity.find('c:resultStatus', namespaces)
        self['Result Status'] = rs.text if rs is not None else ''
        progress = xml_entity.find('c:progress', namespaces)
        self['Progress'] = progress.text if progress is not None else ''
        total = xml_entity.find('c:expectedTotal', namespaces)
        self['Expected Total'] = total.text if total is not None else ''


class MidpointResource(MidpointObject):

    def __init__(self, xml_entity: Element):
        super().__init__()
        self['OID'] = xml_entity.attrib['oid']
        self['Name'] = xml_entity.find('c:name', namespaces).text
        self['Availability Status'] = optional_text(
            xml_entity.find('c:operationalState/c:lastAvailabilityStatus', namespaces))


class MidpointUser(MidpointObject):

    def __init__(self, xml_entity: Element):
        super().__init__()
        self['OID'] = xml_entity.attrib['oid']
        self['Name'] = xml_entity.find('c:name', namespaces).text
        self['FullName'] = optional_text(xml_entity.find('c:fullName', namespaces))
        self['Status'] = xml_entity.find('c:activation/c:effectiveStatus', namespaces).text
        self['EmpNo'] = optional_text(xml_entity.find('c:employeeNumber', namespaces))
        self['Email'] = optional_text(xml_entity.find('c:emailAddress', namespaces))
        self['OU'] = optional_text(xml_entity.find('c:organizationalUnit', namespaces))

        extfields = xml_entity.find('c:extension', namespaces)

        if extfields is not None:
            for extfield in extfields:
                self[re.sub(r'{.*}', '', extfield.tag)] = extfield.text


class MidpointOrganization(MidpointObject):

    def __init__(self, xml_entity: Element):
        super().__init__()
        self['OID'] = xml_entity.attrib['oid']
        self['Name'] = xml_entity.find('c:name', namespaces).text
        self['DisplayName'] = xml_entity.find('c:displayName', namespaces).text
        self['Status'] = xml_entity.find('c:activation/c:effectiveStatus', namespaces).text
        parentorg = xml_entity.find('c:parentOrgRef', namespaces)
        self['Parent'] = None if parentorg is None else parentorg.attrib['oid']


class CustomRetryManager(Retry):

    def __init__(self, **kwargs):
        super(CustomRetryManager, self).__init__(**kwargs)

    def get_backoff_time(self):
        return 2


class MidpointServerError(Exception):
    pass


class MidpointUnsupportedOperation(Exception):
    pass


class RestApiClient:
    def __init__(self, url: str, username: str, password: str):
        self.url = self.sanitize_url(url)
        self.username = username
        self.password = password

        session = requests.Session()

        adapter = HTTPAdapter(max_retries=(CustomRetryManager(connect=1000, total=1000)))
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        self.requests_session = session

    def sanitize_url(self, url: str) -> str:
        parsed_url = urljoin(url, '/midpoint/')
        return parsed_url

    def resolve_rest_type(self, type) -> Optional[str]:
        for end_class, end_rest in endpoints.items():
            if end_class.lower().startswith(type.lower()):
                return end_rest

        raise AttributeError("Can't find REST type for class " + type)

    def get_element(self, element_class: str, element_oid: str) -> Optional[str]:
        rest_type = self.resolve_rest_type(element_class)

        response = self.requests_session.get(url=urljoin(self.url, 'ws/rest/' + rest_type + '/' + element_oid),
                                             auth=(self.username, self.password))

        return response.content.decode()

    def delete(self, element_class: str, element_oid: str) -> str:
        rest_type = self.resolve_rest_type(element_class)

        response = self.requests_session.delete(url=urljoin(self.url, 'ws/rest/' + rest_type + '/' + element_oid),
                                                auth=(self.username, self.password))

        return response.content.decode()

    def get_elements(self, element_class: str) -> Element:
        rest_type = self.resolve_rest_type(element_class)

        response = self.requests_session.get(url=urljoin(self.url, 'ws/rest/' + rest_type),
                                             auth=(self.username, self.password))
        tree = ElementTree.fromstring(response.content)
        return tree

    def execute_action(self, element_class: str, element_oid: str, action: str) -> str:
        rest_type = self.resolve_rest_type(element_class)

        response = self.requests_session.post(
            url=urljoin(self.url, 'ws/rest/' + rest_type + '/' + element_oid + '/' + action),
            auth=(self.username, self.password))

        return response.content

    def put_element(self, xml_filename: str, patch_file: str, patch_write: bool) -> Tuple[str, str]:
        tree_root = self._load_xml(xml_filename)

        object_class = tree_root.tag.split('}', 1)[1] if '}' in tree_root.tag else tree_root.tag  # strip namespace

        if object_class == 'objects':
            raise MidpointUnsupportedOperation('Upload of objects collection is not supported through REST API')

        rest_type = self.resolve_rest_type(object_class)
        object_oid = tree_root.attrib['oid']

        with open(xml_filename, 'r') as xml_file:
            xml_body = xml_file.read()

            if patch_file is not None:
                xml_body = patch_from_file(xml_body, patch_file, patch_write)

            res = self.requests_session.put(url=urljoin(self.url, 'ws/rest/' + rest_type + '/' + object_oid),
                                            data=xml_body,
                                            headers={'Content-Type': 'application/xml'},
                                            auth=(self.username, self.password))

            if res.status_code >= 300:
                raise MidpointServerError('Error ' + str(res.status_code) + ' received from server')

            return object_class, object_oid

    @staticmethod
    def _load_xml(xml_file: str) -> (Element, dict):
        tree_root = ElementTree.parse(xml_file).getroot()
        return tree_root


class TaskExecutionFailure(Exception):
    def __init__(self, message: str):
        super(TaskExecutionFailure).__init__()
        self.message = message

    def __repr__(self):
        return self.message


class AsciiProgressMonitor:
    def __init__(self, width=80, icon='.'):
        self._progress = 0
        self._width = width
        self._icon = icon

    def update(self, progress: int) -> None:
        while self._progress < progress:
            self.advance()

    def advance(self):
        if self._progress % self._width == 0:
            if self._progress > 0:
                print(' %7d' % (self._progress))

            print('Progress: ', end='', flush=True)

        print(self._icon, end='', flush=True)
        self._progress += 1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print()
        print('Total progress:', self._progress)


class MidpointClient:

    def __init__(self, ns: Namespace = None, api_client: RestApiClient = None):
        if ns is not None:
            self.api_client = RestApiClient(ns.url, ns.username, ns.password)

        if api_client is not None:
            self.api_client = api_client

    def __get_collection(self, mp_class: str, local_class: classmethod) -> MidpointObjectList:
        tree = self.api_client.get_elements(mp_class)
        return MidpointObjectList([local_class(entity) for entity in tree])

    def get_tasks(self) -> MidpointObjectList:
        return self.__get_collection('task', MidpointTask)

    def get_resources(self) -> MidpointObjectList:
        return self.__get_collection('resource', MidpointResource)

    def get_users(self) -> MidpointObjectList:
        return self.__get_collection('user', MidpointUser)

    def get_orgs(self) -> MidpointObjectList:
        return self.__get_collection('org', MidpointOrganization)

    def search_users(self, queryterms: List[str]) -> MidpointObjectList:
        users = self.get_users()
        selected_users = self._filter(queryterms, users)
        return selected_users

    def search_orgs(self, queryterms: List[str]) -> MidpointObjectList:
        orgs = self.get_orgs()
        selected_orgs = self._filter(queryterms, orgs)
        return selected_orgs

    def _filter(self, queryterms, mpobjects):
        selected_users = MidpointObjectList()
        for user in mpobjects:
            selected = False

            for uservalue in user.values():
                if uservalue is not None:
                    for term in queryterms:
                        if term.lower() in uservalue.lower():
                            selected = True

            if selected:
                selected_users.append(user)
        return selected_users

    def task_action(self, task_oid: str, task_action: str) -> None:
        self.api_client.execute_action('task', task_oid, task_action)

        if task_action == 'run':
            return self.task_wait(task_oid)

    def task_wait(self, task_oid: str) -> None:
        with AsciiProgressMonitor() as progress:
            while True:
                time.sleep(2)
                task_xml = self.api_client.get_element('task', task_oid)
                task_root = ElementTree.fromstring(task_xml)
                task = MidpointTask(task_root)

                progress.update(int(task['Progress']))

                rstatus = task['Result Status']

                if rstatus != 'in_progress':
                    print()
                    if rstatus != 'success':
                        raise TaskExecutionFailure('Failed execution of task ' + task_oid + ' with status ' + rstatus)

                    break

    def test_resource(self, resource_oid: str) -> None:
        response = self.api_client.execute_action('resource', resource_oid, 'test')
        tree = ElementTree.fromstring(response)
        status = tree.find('c:status', namespaces).text
        return status

    def get_xml(self, type: str, oid: str) -> Optional[str]:
        return self.api_client.get_element(type, oid)

    def put_xml(self, xml_file: str, patch_file: str = None, patch_write: bool = False) -> Tuple[str, str]:
        return self.api_client.put_element(xml_file, patch_file, patch_write)

    def delete(self, type: str, oid: str) -> str:
        return self.api_client.delete(type, oid)
