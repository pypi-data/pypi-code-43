import ntpath
import json
import os
import sys
import time
import re
import traceback
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from api.client_api import AsmAPI


class Handler:
    def __init__(self, host, port, token, timeout=30):
        self.asm_api = AsmAPI(host=host, port=port)
        self.api = self.asm_api.session(token=token, timeout=timeout)
        self.status_ok = 1
        self.status_fail = 0
        self.text_extensions = (".txt", ".xml", ".html")

    def component_identify(self, component):
        if component.startswith('acs-'):
            package_type = 'acs'
        elif component.startswith('alphaopen-adapter'):
            package_type = 'adapters'
        elif component.startswith('admin-'):
            package_type = 'adminapplication'
        elif component.startswith('alphaopen-bridge'):
            package_type = 'bridge'
        elif component.startswith(('jre-', 'bellsoft-jre')):
            package_type = 'jre'
        elif component.startswith('alphaopen-media'):
            package_type = 'mediaserver'
        elif component.startswith('repository'):
            package_type = 'repository'
        elif component.startswith('client-mobile'):
            package_type = 'mobile'
        elif component.startswith('mysql-'):
            package_type = 'mysql'
        elif component.startswith('server-'):
            package_type = 'server'
        elif component.startswith('client-standalone'):
            package_type = 'standaloneclient'
        elif component.startswith('tsdb-'):
            package_type = 'tsdb'
        elif component.startswith('tightvnc-'):
            package_type = 'vncserver'
        else:
            return self.status_fail

        return package_type

    def upload(self, package):
        self.api.upload(package)
        return self.status_ok

    def download(self, url):
        self.api.download(url)
        return self.status_ok

    def install(self, package):
        try:
            dist_path = (self.api.get_path() + r'/var/distfiles')
            package_type = Handler.component_identify(self, component=package)
            if not package_type:
                return self.status_fail
            full_path = ("{}/{}/{}".format(dist_path, package_type, package))
            install_package = self.api.install(path=full_path)

            return install_package['detail']['printable_id']

        except ValueError as exception:
            return exception

    def get_path(self, component=False):
        if component:
            return self.api.get_component(component)['detail']['home']
        return self.api.get_path()

    def set_task(self, component, key, value):
        return self.api.set_task(component, key, value)

    def set_alias(self, component, alias):
        return self.api.set_task(component, 'alias', alias)

    def set_json(self, key, value, component):
        request_get_component_json = self.api.get_component(component)
        component_properties = json.loads(json.dumps(request_get_component_json))

        try:
            if key in component_properties:
                self.api.set_json(component, key, value)
        except ValueError as exception:
            return exception

        return self.status_ok

    def set_xml(self, component, xml, value):
        writefile = os.path.join(Handler.get_path(self, component), ntpath.normpath(xml))

        if value.lower().endswith(self.text_extensions):
            with open(value, mode='rb') as read_file:
                content = read_file.read()
        else:
            content = value.encode()
        self.api.set_xml(component, writefile, content)
        return self.status_ok

    def get_xml(self, component, xml):
        return self.api.get_xml(component, xml)['content']

    def get_component(self, component, prop='all'):
        try:
            component_json = json.loads(json.dumps(self.api.get_component(component)))
            if prop == 'all':
                return component_json
            return component_json[prop]
        except (ValueError, KeyError):
            traceback.print_exc()
            return None

    def get_files(self, prop='all'):
        json_files_dist = json.loads(json.dumps(self.api.get_files()))

        value_list = []
        for value in json_files_dist['tree']:
            value_list.append(value)

        files_return = []

        for item in value_list:
            if item['children']:
                children = item['children']
                if prop in (item['name'], 'all'):
                    for child in children:
                        files_return.append(ntpath.split(child['path'])[1])

        return files_return

    def get_users(self, user='all'):
        try:
            request_get_users = json.loads(json.dumps(self.api.get_users()))

            users = ''
            if user == 'all':
                users = request_get_users
                #users = json.dumps(request_get_users, ensure_ascii=False)
            else:
                for asm_user in request_get_users:
                    user_properties = json.loads(json.dumps(asm_user, ensure_ascii=False))
                    if user_properties['username'] == user:
                        users = asm_user

            return users

        except (ValueError, KeyError) as exception:
            return exception

    def get_conf(self, prop='all'):
        conf = self.api.get_conf()

        if prop == 'all':
            return conf
        try:
            return (json.loads(json.dumps(conf, ensure_ascii=False)))[prop]
        except (ValueError, KeyError) as exception:
            return exception

    def set_conf(self, prop, value):
        return self.api.set_conf(prop, value)

    def get_task(self, prop='all'):
        task_list = []
        try:
            if prop == 'all':
                for task in json.loads(json.dumps(self.api.get_task())):
                    task_list.append(task['printable_id'])
            elif '_' in prop:
                tasks = json.loads(json.dumps(self.api.get_task(prop)))
                task_list = tasks
                # for key, value in tasks.items():
                #     task_list.append("'{}': '{}'".format(key, value))
            else:
                for task in json.loads(json.dumps(self.api.get_task())):
                    if (task['printable_id'].split('_'))[0] == prop:
                        task_list.append(task['printable_id'])
            return task_list
        except (ValueError, KeyError) as exception:
            return exception

    def delete_files(self, prop):
        package_type = Handler.component_identify(self, component=prop)
        if not package_type:
            return "Failed to identify component type of {}".format(prop)
        dist_path = (self.api.get_path() + r'/var/distfiles')
        path = "{}/{}/{}".format(dist_path, package_type, prop)
        self.api.delete_file(path)
        return self.status_ok

    def delete_task(self, prop):
        self.api.delete_component(prop)
        return self.status_ok

    def action(self, component, command):
        if command == 'start':
            command = 'run'
        elif command == 'script':
            command = 'createScript'
        elif command == 'restart':
            command = 'rerun'

        if component == "all":
            for asm_component in self.get_task():
                if command in ('rerun', 'stop'):
                    current_status = self.get_component(asm_component, 'detail')["current_status"]
                    status = self.get_component(asm_component, 'detail')["status"]
                    if "running" in (current_status, status):
                        self.api.actions(asm_component, command)
                else:
                    self.api.actions(asm_component, command)
        else:
            self.api.actions(component, command)

        return self.status_ok

    def restart(self, component):
        return self.api.actions(component, 'rerun')

    def start(self, component):
        return self.api.actions(component, 'run')

    def stop(self, component):
        return self.api.actions(component, 'stop')

    def create_script(self, component):
        return self.api.actions(component, 'createScript')

    def kill(self, pid):
        return self.api.kill(pid)

    def get_log(self, component, path):
        try:
            if component.lower() != "asm":
                component_type, component_id = component.split('_')

            if not path.endswith(('.zip', '.log')):
                if component.lower() != "asm":
                    filename = '{}-{}.log.zip'.format(component_type, component_id)
                else:
                    if self.api.get_info()['os_name'].lower() == "windows":
                        filename = 'service.log'
                    else:
                        filename = 'asm.django.log'
                path = os.path.join(path, filename)

            result = self.api.log(component, path)
            if not result:
                return path
            return self.status_fail
        except ValueError as exception:
            return exception

    def set_rules(self, path):
        return self.api.set_rules(path)

    def get_rules(self):
        rules = (json.loads(json.dumps(self.api.get_rules())))['executable']
        return rules

    def get_info(self, prop='all'):
        info = self.api.get_info()
        try:
            del info['processes']
        except KeyError:
            pass
        if prop == 'all':
            return info
        return info[prop]

    def get_export(self):
        return self.api.get_export()

    def get_process(self, prop=None, key=None, value=None):
        processes = self.api.get_info()['processes']
        if not bool(prop or key or value):
            return processes

        return_proc = []
        if key and value:
            for process in processes:
                if str(process[key]) == value:
                    if prop != 'all':
                        try:
                            return_proc.append(process[prop])
                        except (ValueError, KeyError):
                            traceback.print_exc()
                    else:
                        return_proc.append(process)
        else:
            if prop != 'all':
                for process in processes:
                    try:
                        return_proc.append(process[prop])
                    except (ValueError, KeyError):
                        traceback.print_exc()
            else:
                return processes

        return return_proc

    def get_alias(self, component='all'):
        tasks = self.api.get_task()
        aliases = {}
        for task in tasks:
            alias = task['alias']
            printable_id = task['printable_id']
            if alias:
                if component == 'all':
                    aliases[alias] = printable_id
                elif alias == component:
                    return printable_id
                elif printable_id == component:
                    return alias
        return aliases

    def lib_upload(self, path):
        try:
            self.api.lib_upload(path)
        except Exception:
            traceback.print_exc()
        return self.status_ok

    def lib_files(self, lib=None):
        libs = self.api.get_requirements()['packages']
        if not lib:
            return libs

        return_list = []
        for library in libs:
            if library.startswith(lib):
                return_list.append(library)
        return return_list

    def lib_freeze(self, lib=None):
        libs = self.api.get_requirements()['installed']
        return_list = []
        if not lib:
            for library in libs:
                return_list.append("{}=={}".format(library['name'], library['version']))
        else:
            for library in libs:
                if library['name'] == lib:
                    return_list.append(library['version'])
        return return_list

    def lib_list(self):
        libs = self.api.get_requirements()['installed']
        return_list = []
        for library in libs:
            return_list.append(library['name'])
        return return_list

    def lib_version(self, lib):
        libs = self.api.get_requirements()['installed']
        for library in libs:
            if library['name'] == lib:
                return library['version']

    def lib_install(self, lib):
        if lib in self.lib_files():
            self.api.lib_install(lib)
        else:
            return self.status_fail
        return self.status_ok

    def identify_last_version(self, lst):
        try:
            lst.sort(reverse=True, key=lambda s: map(int, s.split('.')))
            return lst[0]
        except (ValueError, KeyError) as exception:
            return exception

    def cert_upload(self, path):
        try:
            self.api.truststore_upload(path)
        except Exception:
            traceback.print_exc()
        time.sleep(1)
        return self.status_ok

    def cert_info(self):
        return self.api.truststore_info()['truststore']

    def cert_list(self):
        truststore_list = Handler.cert_info(self)
        re1 = '(alpha-\d+),'
        rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
        return rg.findall(truststore_list)

    def download_certificate(self, path):
        if not path.endswith('.crt'):
            path = os.path.join(path, 'service.crt')
        self.api.download_certificate(path)
        return self.status_ok

    def download_truststore(self, path):
        self.api.download_truststore(path)
        return self.status_ok

    def remove_certificate(self, alias):
        try:
            self.api.remove_certificate(alias)
        except Exception:
            traceback.print_exc()
        time.sleep(1)
        return self.status_ok
