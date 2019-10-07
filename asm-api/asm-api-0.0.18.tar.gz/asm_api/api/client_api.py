import requests
import json
import functools
import ntpath
import os
from base64 import b64encode

try:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    import urllib3
    urllib3.disable_warnings()


class AsmAPIRequestException(Exception):
    def __init__(self, message):
        message = 'Unacceptable status, the operation will be interrupted. {}'.format(message)
        super(AsmAPIRequestException, self).__init__(message)


class AsmAPIValueException(Exception):
    def __init__(self):
        message = 'Unacceptable value, the operation will be interrupted.'
        super(AsmAPIValueException, self).__init__(message)


class Session(object):
    def __init__(self, api, session):
        self.api = api
        self.session = session

    def __getattr__(self, attr):
        assert attr != 'session'
        api_method = getattr(self.api, attr)
        return functools.partial(api_method, self.session)


class AsmAPI:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.base_url = 'https://{}:{}'.format(host, port)

        self.asm_api_files_upload_dist = '{}/api/files/upload/dist/'.format(self.base_url)
        self.asm_api_files_upload_requirements = '{}/api/files/upload/requirements/'.format(self.base_url)
        self.asm_api_files_upload_truststore = '{}/api/files/upload/truststore/'.format(self.base_url)
        self.asm_api_files_download = '{}/api/files/download/'.format(self.base_url)
        self.asm_api_files_download_certificate = '{}/api/files/download/certificate/'.format(self.base_url)
        self.asm_api_files_download_truststore = '{}/api/files/download/truststore/'.format(self.base_url)
        self.asm_api_files_truststore_alias = '{}/api/files/truststore/{}/'.format(self.base_url, '{}')
        self.asm_api_files_dist = '{}/api/files/dist/'.format(self.base_url)
        self.asm_api_files_install = '{}/api/files/install/'.format(self.base_url)
        self.asm_api_files_truststore = '{}/api/files/truststore/'.format(self.base_url)
        self.asm_api_components = '{}/api/components/'.format(self.base_url)
        self.asm_api_task = '{}/api/task/'.format(self.base_url)
        self.asm_api_user_create = '{}/api/user/create/'.format(self.base_url)
        self.asm_api_user_remove = '{}/api/user/remove/'.format(self.base_url)
        self.asm_api_user = '{}/api/user/'.format(self.base_url)
        self.asm_api_rules = '{}/api/rules/'.format(self.base_url)
        self.asm_api_conf = '{}/api/conf/'.format(self.base_url)
        self.asm_api_conf_requirements = '{}/api/conf/requirements/'.format(self.base_url)
        self.asm_api_info = '{}/api/monitor/info/'.format(self.base_url)
        self.asm_api_dump_file = '{}{}/{}/dump_file/'.format(self.asm_api_components, '{}', '{}')
        self.asm_api_upgrade = '{}{}/{}/upgrade/'.format(self.asm_api_components, '{}', '{}')
        self.asm_api_monitor_kill = '{}/api/monitor/kill/{}/'.format(self.base_url, '{}')
        self.asm_api_monitor_exported = '{}/api/monitor/exported/'.format(self.base_url)

        self.status_ok = 1
        self.status_fail = 0

    def session(self, token, timeout=30):
        asm_session = requests.Session()

        asm_session.verify = False
        asm_session.timeout = timeout

        asm_session.headers.update({'authorization': 'Token {}'.format(token)})

        r = asm_session.get(self.base_url + '/login', timeout=10)
        r.raise_for_status()

        asm_session.headers.update({'X-CSRFToken': r.cookies['csrftoken']})

        #asm_session.cookies.update({'sessionid':'13245177708363586587'})

        return Session(api=self, session=asm_session)

    def actions(self, session, component, command):
        component_type, component_id = component.split('_')

        data = {'id': component_id, 'action': command}

        r = session.post('{}{}/{}/'.format(self.asm_api_task, component_id, command), data=data)
        r.raise_for_status()

        return self.status_ok

    def set_conf(self, session, prop, value):
        data = dict()
        data[prop] = value
        json_data = json.loads(json.dumps(data))

        r = session.post(self.asm_api_conf, json=json_data)
        r.raise_for_status()

        return self.status_ok

    def delete_component(self, session, component):
        try:
            component_type, component_id = component.split('_')
            url = '{}/{}/{}/'.format(self.asm_api_components, component_type.lower(), component_id)
        except:
            raise AsmAPIValueException()

        r = session.delete(url)
        r.raise_for_status()

        return self.status_ok

    def delete_file(self, session, path):
        r = session.post(self.asm_api_files_dist, json=[path])
        r.raise_for_status()

        return self.status_ok

    def download(self, session, url):
        data = {'link': url}
        r = session.post(self.asm_api_files_download, data=data)
        r.raise_for_status()

        return self.status_ok

    def get_path(self, session):
        json_files_dist = json.loads(json.dumps(AsmAPI.get_files(self, session)))
        asm_path = ntpath.split(ntpath.split(ntpath.split(json_files_dist['tree'][0]['path'])[0])[0])[0]

        return asm_path

    def get_components(self, session, component):
        url = "{}{}/".format(self.asm_api_components, component)

        r = session.get(url)
        r.raise_for_status()

        return r.json()

    def get_component(self, session, component):
        try:
            component_type, component_id = component.split('_')
            url = "{}{}/{}".format(self.asm_api_components, component_type, component_id)
        except:
            raise AsmAPIValueException()

        r = session.get(url)
        r.raise_for_status()

        return r.json()

    def get_files(self, session):
        r = session.get(self.asm_api_files_dist)
        r.raise_for_status()

        return r.json()

    def get_users(self, session):
        r = session.get(self.asm_api_user)
        r.raise_for_status()

        return r.json()

    def get_conf(self, session):
        r = session.get(self.asm_api_conf)
        r.raise_for_status()

        return r.json()

    def get_info(self, session):
        r = session.get(self.asm_api_info)
        r.raise_for_status()

        return r.json()

    def get_rules(self, session):
        r = session.get(self.asm_api_rules)
        r.raise_for_status()

        return r.json()

    def kill(self, session, pid):
        data = {'action':'kill', 'pid':pid}
        r = session.post(self.asm_api_monitor_kill.format(pid), json=data)
        r.raise_for_status()

        return self.status_ok

    def get_task(self, session, component=None):
        if component:
            if len(component.split('_')) > 2:
                raise AsmAPIValueException

            try:
                component_type, component_id = component.split('_')
                url = "{}{}".format(self.asm_api_task, component_id)
            except ValueError:
                url = "{}{}".format(self.asm_api_task, component)
        else:
            url = "{}".format(self.asm_api_task)

        r = session.get(url)
        r.raise_for_status()

        return r.json()

    def install(self, session, path):
        data = {'path': path}
        r = session.post(self.asm_api_files_install, data=data)
        r.raise_for_status()

        return r.json()

    def log(self, session, component, path):
        if component.lower() != "asm":
            try:
                component_type, component_id = component.split('_')
            except:
                raise AsmAPIValueException()
            url = "{}{}/{}/log_file/".format(self.asm_api_components, component_type.lower(), component_id)
        else:
            if self.get_info(session)['os_name'].lower() == "windows":
                filename = 'service.log'
            else:
                filename = 'asm.django.log'
            url = "{}root/?filename={}".format(self.asm_api_files_download, filename)
        
        session.stream = True

        r = session.get(url)
        r.raise_for_status()

        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        return self.status_ok

    def set_task(self, session, component, key, value):
        try:
            component_type, component_id = component.split('_')
        except:
            raise AsmAPIValueException()

        url = "{}{}/".format(self.asm_api_task, component_id)

        data = {key: value}

        r = session.put(url, json=data)
        r.raise_for_status()

        return self.status_ok

    def set_rules(self, session, path):
        if os.path.isdir(path) or os.path.isfile(path):
            with open(path, mode='rb') as rf:
                value = rf.read().decode('utf-8')
        else:
            value = path

        data = {'sandbox': value}

        r = session.post(self.asm_api_rules, json=data)
        r.raise_for_status()

        r = session.put(self.asm_api_rules, json=data)
        r.raise_for_status()

        return self.status_ok

    def set_json(self, session, component, prop, value):
        try:
            component_type, component_id = component.split('_')
            component_api_url = "{}/api/components/{}/{}/".format(self.base_url, component_type.lower(), component_id)
        except:
            raise AsmAPIValueException()

        data = dict()
        data[prop] = value
        json_data = json.loads(json.dumps(data))

        r = session.put(component_api_url, data=json_data)
        r.raise_for_status()

        return self.status_ok

    def set_xml(self, session, component, xml, content):
        try:
            component_type, component_id = component.split('_')
        except:
            raise AsmAPIValueException()

        url = "{}/api/components/{}/{}/edit_file/".format(self.base_url, component_type.lower(), component_id)

        data = {'content': content, 'filename': xml}
        
        r = session.post(url, json=data)

        r.raise_for_status()

        return self.status_ok

    def get_xml(self, session, component, xml):
        try:
            component_type, component_id = component.split('_')
        except:
            raise AsmAPIValueException()

        url = "{}/api/components/{}/{}/edit_file/".format(self.base_url, component_type.lower(), component_id)
        home = self.get_task(session, component)['home']
        xml_path = ntpath.join(home, ntpath.normpath(xml))
        data = {"filename":xml_path, "content":None}

        r = session.post(url, json=data)

        r.raise_for_status()

        return r.json()

    def upload(self, session, path):
        file = {'file': open(path, mode='rb')}

        r = session.post(self.asm_api_files_upload_dist, files=file)
        r.raise_for_status()

        return self.status_ok

    def dump_post(self, session, component, path):
        try:
            file = {'file': open(path, mode='rb')}
        except OSError:
            file = {'file': path}

        try:
            component_type, component_id = component.split('_')
            component_api_url = self.asm_api_dump_file.format(component_type.lower(), component_id)
        except ValueError:
            raise AsmAPIValueException()

        r = session.post(component_api_url, files=file)
        r.raise_for_status()

        return self.status_ok

    def dump_get(self, session, component):
        try:
            component_type, component_id = component.split('_')
            component_api_url = self.asm_api_dump_file.format(component_type.lower(), component_id)
        except:
            raise AsmAPIValueException()

        r = session.get(component_api_url)
        r.raise_for_status()

        return r.content

    def upgrade(self, session, component, path):
        try:
            component_type, component_id = component.split('_')
            component_api_url = self.asm_api_upgrade.format(component_type.lower(), component_id)
        except:
            raise AsmAPIValueException()

        r = session.post(component_api_url, data=path)
        r.raise_for_status()

        return self.status_ok

    def lib_upload(self, session, path):
        file = {'file': open(path, mode='rb')}

        r = session.post(self.asm_api_files_upload_requirements, files=file)
        r.raise_for_status()

        return self.status_ok

    def lib_install(self, session, package):
        data = {"package": package}

        r = session.post(self.asm_api_conf_requirements, json=data)
        r.raise_for_status()

        return r.text

    def get_requirements(self, session):
        r = session.get(self.asm_api_conf_requirements)
        r.raise_for_status()

        return r.json()

    def truststore_upload(self, session, path):
        file = {'file': open(path, mode='rb')}

        r = session.post(self.asm_api_files_upload_truststore, files=file)
        r.raise_for_status()

        return self.status_ok

    def truststore_info(self, session):
        r = session.get(self.asm_api_files_truststore)
        r.raise_for_status()

        return r.json()

    def download_certificate(self, session, path):
        session.stream = True

        r = session.get(self.asm_api_files_download_certificate)
        r.raise_for_status()

        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        return self.status_ok

    def download_truststore(self, session, path):
        session.stream = True

        r = session.get(self.asm_api_files_download_truststore)
        r.raise_for_status()

        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        return self.status_ok

    def remove_certificate(self, session, alias):
        r = session.delete(self.asm_api_files_truststore_alias.format(alias))
        r.raise_for_status()

        return self.status_ok

    def get_export(self, session):
        r = session.get(self.asm_api_monitor_exported)
        r.raise_for_status

        return r.json()
