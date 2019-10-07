import sys
import ntpath
import json
import traceback
import re
import os
sys.path.append(ntpath.dirname(ntpath.abspath(__file__)))
from asm_api.asm_api import Handler
from clparser import CreateParser
from os import path, listdir
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

try:
    import urllib3
    urllib3.disable_warnings()
except ImportError:
    pass

###########
# # CLI Import example

# import os
# import sys
# from asm_cli import asm

# BASE_PATH=os.path.dirname(os.path.abspath(__file__))

# if sys.platform.startswith('win32'):
#     BASE_PATH=os.path.dirname(BASE_PATH)
    
# ASM=asm.ServiceManager(os.path.join(BASE_PATH,"cli-settings.ini"))
# ASM.cli()
###########

class ServiceManager:
    def __init__(self, settings_file=None):
        self.parser = CreateParser(settings_file).create_parser()
        self.valuespace = self.parser.parse_args(sys.argv[1:])

        if len(sys.argv[1:])==0:
            self.parser.print_help()
            self.parser.exit()

        main_args = ['host', 'port', 'token', 'timeout', 'command']
        args = vars(self.parser.parse_args())
        for arg in main_args:
            del args[arg]

        if not self.valuespace.token or self.valuespace.token == "0":
            if settings_file:
                try:
                    config_file = ConfigParser.ConfigParser()
                    config_file.read(settings_file)
                    self.valuespace.token = config_file.get(self.valuespace.host, 'TOKEN')
                except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as exception:
                    print("{}. Token (--token) must be specified.".format(exception))
                    sys.exit(1)
            else:
                print("Token (--token) must be specified.")
                sys.exit(1)


        self.asm = Handler(host=self.valuespace.host,
                      port=self.valuespace.port,
                      token=self.valuespace.token,
                      timeout=self.valuespace.timeout)


    def json_print(self, value):
        print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False).encode('utf-8'))

    # def all_aliases(self , alias):
    #     all_aliases_list = ["all_services", "all_adapters", "all_bridges", "all_mysql",\
    #         "all_media_services", "all_servers", "all_tsdb", "all_repositories", "all_acs",\
    #         "all_web_services", "all_ta_api", "all_adminapplication", "all_standaloneclient", "all_files", "all_files_services", "all_files_adapters",\
    #         "all_files_bridges", "all_files_mysql", "all_files_media_services", "all_files_servers",\
    #         "all_files_tsdb", "all_files_repositories", "all_files_acs", "all_files_web_services", "all_files_ta_api"]
    #     if alias in all_aliases_list:
    #         if "files" in alias:
    #             return
    #         elif:
    #             if prop == 'all_services':
    #                 result = asm.get_task("all")
    #             elif prop = 'all_files':
    #                 result = asm.get_files("all")
    #             else:
    #                 _, component_type = alias.split('_'):
    #                 if component_type = "adapters":
    #                     component_type = "adapter"
    #                 elif component_type = "servers":
    #                     component_type = "server"
    #                 elif component_type = "tsdb":
    #                     component_type = "tsdbserver"
    #                 elif component_type = "repositories":
    #                     component_type = "repositoryserver"
    #                 elif component_type = "servers":
    #                     component_type = "server"
    #                 elif component_type = "servers":
    #                     component_type = "server"
    #                 elif component_type = "servers":
    #                     component_type = "server"
    #                 elif component_type = "servers":
    #                     component_type = "server"
    #                 elif component_type = "servers":
    #                     component_type = "server"
    #                 elif component_type = "servers":
    #                     component_type = "server"

    def is_alias(self, component):
        aliases = self.asm.get_alias()
        if component in aliases:
            return aliases[component]
        return None

    def cli(self):
        asm = self.asm
        valuespace = self.valuespace
        parser = self.parser

        json_print = self.json_print
        is_alias = self.is_alias

        if valuespace.command == "upload":
            if valuespace.file:
                for package in valuespace.file:
                    if package.endswith(('zip', 'tar.gz')):
                        asm.upload(package)
                    else:
                        onlyfiles = [f for f in listdir(package) if path.isfile(path.join(package, f))]
                        for f in onlyfiles: 
                            asm.upload(path.join(package, f))
            else:
                print("At least 1 file (-f/--file) must be specified.")
                sys.exit(1)

        elif valuespace.command == "download":
            for url in valuespace.url:
                if valuespace.auth:
                    url = url.replace("://", "://{}@".format(valuespace.auth))
                result = asm.download(url)
                if result != asm.status_ok:
                    print(result)

        elif valuespace.command == "install":
            if valuespace.package:
                for package in valuespace.package:
                    result = asm.install(package)
                    if result != asm.status_fail:
                        print(result)
                    else:
                        print('An error occurred while installing "{}".'.format(package))
            else:
                print("At least 1 package (-p/--package) must be specified.")
                sys.exit(1)

        elif valuespace.command == "set":
            if valuespace.component:
                if valuespace.key:
                    if valuespace.value:
                        for component in valuespace.component:
                            component_id = is_alias(component)
                            if component_id:
                                component = component_id
                            if valuespace.key.lower().endswith(asm.text_extensions):
                                result = asm.set_xml(component, valuespace.key, valuespace.value)
                            else:
                                result = asm.set_json(valuespace.key, valuespace.value, component)
                            if result != asm.status_ok:
                                print(result)
                    else:
                        print("Value (-v/--value) must be specified.")
                        sys.exit(1)
                else:
                    print("Key (-k/--key) must be specified.")
                    sys.exit(1)
            else:
                print("At least 1 component (-c/--component) must be specified.")
                sys.exit(1)

        elif valuespace.command == "get":
            if valuespace.component:
                if not valuespace.property:
                    valuespace.property = ["all"]
                for component in valuespace.component:
                    if component.lower() == 'files':
                        for prop in valuespace.property:
                            result = asm.get_files(prop)
                            if result != asm.status_fail:
                                for package in result:
                                    print(package)
                            else:
                                print(result)

                    elif component.lower() == 'users':
                        for user in valuespace.property:
                            result = asm.get_users(user)
                            if isinstance(result, list):
                                for asm_user in result:
                                    print()
                                    json_print(asm_user)
                            else:
                                json_print(result)

                    elif component.lower() == 'conf':
                        for prop in valuespace.property:
                            result = asm.get_conf(prop)
                            if prop == 'all':
                                json_print(result)
                            else:
                                print(result)

                    elif component.lower() == 'task':
                        for prop in valuespace.property:
                            component_id = is_alias(prop)
                            if component_id:
                                prop = component_id
                            result = asm.get_task(prop)
                            if result != asm.status_fail:
                                if isinstance(result, dict):
                                    json_print(result)
                                elif isinstance(result, list):
                                    for task in result:
                                        print(task)
                                else:
                                    print(result)
                            else:
                                print(result)

                    elif component.lower() == "export":
                        result = asm.get_export()
                        if result != asm.status_fail:
                            json_print(result)

                    else:
                        component_id = is_alias(component)
                        if component_id:
                            component = component_id
                        for prop in valuespace.property:
                            if prop.lower().endswith(asm.text_extensions):
                                result = asm.get_xml(component, prop)
                            else:
                                result = asm.get_component(component, prop)
                            if result:
                                if isinstance(result, dict):
                                    json_print(result)
                                else:
                                    print(result)
            else:
                print("At least 1 component (-c/--component) must be specified.")
                sys.exit(1)

        elif valuespace.command == "delete":
            if valuespace.component:
                # if "all" in valuespace.component:
                #     result = asm.delete_files("all")
                #     if result != asm.status_ok:
                #         print(result)
                # elif:
                for component in valuespace.component:
                    if component.endswith(('zip', 'tar.gz')):
                        result = asm.delete_files(component)
                        if result != asm.status_ok:
                            print(result)
                    else:
                        component_id = is_alias(component)
                        if component_id:
                            component = component_id
                        result = asm.delete_task(component)
                        if result != asm.status_ok:
                            print(result)
            else:
                print("At least 1 component (-c/--component) must be specified.")
                sys.exit(1)

        elif valuespace.command == "start" \
                or valuespace.command == "stop"\
                or valuespace.command == "restart"\
                or valuespace.command == "script":
            if valuespace.component:
                if "all" in valuespace.component:
                    result = asm.action("all", valuespace.command)
                    if result != asm.status_ok:
                        print(result)
                else:
                    for component in valuespace.component:
                        component_id = is_alias(component)
                        if component_id:
                            component = component_id
                        if len(component.split("_")) == 2:
                            result = asm.action(component, valuespace.command)
                            if result != asm.status_ok:
                                print(result)
                        else:
                            components_list = asm.get_task(component)
                            for component in components_list:
                                result = asm.action(component, valuespace.command)
                                if result != asm.status_ok:
                                    print(result)
            else:
                print("At least 1 component (-c/--component) must be specified.")
                sys.exit(1)

        elif valuespace.command == "kill":
            result = asm.kill(valuespace.pid)
            if result != asm.status_ok:
                print(result)

        elif valuespace.command == "log":
            if valuespace.component:
                if valuespace.path:
                    for component in valuespace.component:
                        component_id = is_alias(component)
                        if component_id:
                            component = component_id
                        result = asm.get_log(component, valuespace.path)
                else:
                    print("Path (-p/--path) must be specified.")
                    sys.exit(1)
            else:
                print("At least 1 component (-c/--component) must be specified.")
                sys.exit(1)

        elif valuespace.command == "info":
            for prop in valuespace.property:
                result = asm.get_info(prop)
                if isinstance(result, dict):
                    json_print(result)
                else:
                    print(result)

        elif valuespace.command == "process":
            if valuespace.key:
                if not valuespace.value:
                    parser.error("Value -v/--value not specified.")
            if valuespace.value:
                if not valuespace.key:
                    valuespace.key = "pid"

            result = asm.get_process(valuespace.property, valuespace.key, valuespace.value)
            if isinstance(result, dict):
                json_print(result)
            elif isinstance(result, list):
                for item in result:
                    print(item)
            else:
                print(result)


        elif valuespace.command == "rules":
            if valuespace.get:
                print(asm.get_rules())
            elif valuespace.set != None:
                result = asm.set_rules(valuespace.set)
                if result != asm.status_ok:
                    print(result)
            elif valuespace.enable:
                asm.set_conf("enable_rules", True)
            elif valuespace.disable:
                asm.set_conf("enable_rules", False)
            else:
                parser.error('No arguments provided.')

        elif valuespace.command == "conf":
            asm.set_conf(valuespace.key, valuespace.value)

        elif valuespace.command == "alias":
            component = valuespace.component
            alias = valuespace.alias

            component_id = is_alias(component)
            if component_id:
                component = component_id
            result = asm.set_alias(component, alias)
            if result != asm.status_ok:
                print(result)

        elif valuespace.command == "task":
            if not valuespace.component:
                if not bool(valuespace.key and valuespace.value and not valuespace.component):
                    if not bool(valuespace.component and (valuespace.value or valuespace.key)):
                        valuespace.component = ["all"]
                    else:
                        if not valuespace.component:
                            parser.error("Component -c/--component not specified.")
                        if valuespace.value and not valuespace.key:
                            parser.error("Key -k/--key not specified.")
                else:
                    parser.error("Component -c/--component not specified.")
            for component in valuespace.component:
                component_id = is_alias(component)
                if component_id:
                    component = component_id
                if not bool(valuespace.value or valuespace.key):
                    result = asm.get_task(component)
                    if result and result != asm.status_fail:
                        if isinstance(result, dict):
                            json_print(result)
                        elif isinstance(result, list):
                            for task in result:
                                print(task)
                        else:
                            print(result)
                    else:
                        print(result)
                elif not valuespace.value:
                    result = asm.get_task(component)
                    if result:
                        if isinstance(result, list):
                            for res in result:
                                res_value = asm.get_task(res)[valuespace.key]
                                if res_value: print(res_value)
                        else:
                            try:
                                res = result[valuespace.key]
                                if res: print(result[valuespace.key])
                            except KeyError as exception:
                                traceback.print_exc()
                else:
                    if valuespace.key:
                        result = asm.set_task(component, valuespace.key, valuespace.value)
                        if result != asm.status_ok:
                            print(result)
                    else:
                        parser.error("Key -k/--key not specified.")

        elif valuespace.command == "lib":
            if valuespace.upload != None:
                for lib in valuespace.upload:
                    if lib.endswith(('zip', 'tar.gz')):
                        asm.lib_upload(lib)
                    else:
                        onlyfiles = [f for f in listdir(lib) if path.isfile(path.join(lib, f))]
                        for f in onlyfiles: 
                            asm.lib_upload(path.join(lib, f))
            elif valuespace.files != None:
                if len(valuespace.files) == 0:
                    valuespace.files = ['all']
                for lib in valuespace.files:
                    if lib.lower() == 'all':
                        lib = None
                    result= asm.lib_files(lib)
                    for item in result:
                        print(item)
            elif valuespace.list:
                result= asm.lib_list()
                for item in result:
                    print(item)
            elif valuespace.version:
                for lib in valuespace.version:
                    print(asm.lib_version(lib))
            elif valuespace.install != None:
                for lib in valuespace.install:
                    result = asm.lib_install(lib)
                    if result == asm.status_fail:
                        print('Error: no such package - "{}"!'.format(lib))
            elif valuespace.freeze:
                result= asm.lib_freeze()
                for item in result:
                    print(item)
            else:
                parser.error('No arguments provided.')

        elif valuespace.command == "cert":
            if valuespace.upload != None:
                for cert in valuespace.upload:
                    if cert.endswith('.crt'):
                        asm.cert_upload(cert)
                    else:
                        onlyfiles = [f for f in listdir(cert) if path.isfile(path.join(cert, f))]
                        for f in onlyfiles: 
                            if f.endswith('.crt'):
                                asm.cert_upload(path.join(cert, f))
            elif valuespace.info:
                print(asm.cert_info())
            elif valuespace.list:
                for item in asm.cert_list():
                    print(item)
            elif valuespace.download != None:
                asm.download_certificate(valuespace.download)
            elif valuespace.truststore != None:
                asm.download_truststore(valuespace.truststore)
            elif valuespace.remove != None:
                for cert in valuespace.remove:
                    asm.remove_certificate(cert)
            else:
                parser.error('No arguments provided.')



        # elif valuespace.command == "xml":
        #     if valuespace.component:
        #         if valuespace.file:
        #             if valuespace.value:
        #                 for component in valuespace.component:
        #                     result = asm.set_xml(component, valuespace.file, valuespace.value)
        #                     if result != asm.status_ok:
        #                         print(result)
        #             else:
        #                 print("Value (-v/--value) must be specified.")
        #         else:
        #             print("File (-f/--file) must be specified.")
        #             sys.exit(1)
        #     else:
        #         print("At least 1 component (-c/--component) must be specified.")
        #         sys.exit(1)
        