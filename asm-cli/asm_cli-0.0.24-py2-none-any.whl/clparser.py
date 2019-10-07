import argparse
import os
import sys
import re
from asm_api.__init__ import __version__ as asm_api_version
from asm_cli.__init__ import __version__ as asm_cli_version
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser


def arg_main(sub, default_host, default_port, default_token, default_timeout):
    sub.add_argument('--host', '-o', default=default_host, type=str,
                     help = 'ASM IP Address', metavar='[ip]')
    sub.add_argument('--port', default=default_port, type=str,
                     help='ASM Port', metavar='port')
    sub.add_argument('--token', type=str,
                     help='ASM Token', metavar='token')
    sub.add_argument('--timeout', default=default_timeout, type=str,
                     help='Request timeout', metavar='timeout')


def arg_component(sub):
    sub.add_argument('-c', '--component', type=str, nargs='+',
                     help='ASM component name (e.g. "adapter_1")', metavar='[component_id]')


def arg_property(sub):
    sub.add_argument('-p', '--property', type=str, nargs='+',
                     help='ASM component property name (e.g. "port")', metavar='[property]')


class CreateParser:
    def __init__(self, settings_file=None):
        self.version = '2.8.5'

        cf = None
        if settings_file:
            cf = ConfigParser()
            cf.read(settings_file)

        # set default ip
        try:
            if cf:
                self.default_host = str(cf.get('SETTINGS', 'IP'))
            else:
                raise
        except Exception:
            self.default_host = "127.0.0.1"

        # set default port
        try:
            if cf:
                self.default_port = str(cf.get('SETTINGS', 'PORT'))
            else:
                raise
        except Exception:
            self.default_port = "8000"

        # set default token
        try:
            if cf:
                self.default_token = str(cf.get(self.default_host, 'TOKEN'))
            else:
                raise
        except Exception:
            self.default_token = "0"

        # set default timeout
        try:
            if cf:
                self.default_timeout = str(cf.get('SETTINGS', 'TIMEOUT'))
            else:
                raise
        except Exception:
            self.default_timeout = "30"


    def create_parser(self):
        dh, dp, dt, dtm = self.default_host, self.default_port, self.default_token, self.default_timeout

        parser = argparse.ArgumentParser(
            prog='ASM',
            description='Alphalogic Service Manager command line interface.',
            epilog='(c) 2019 Alphaopen LLC | www.alphaopen.com',
            add_help=False,
            formatter_class=argparse.RawTextHelpFormatter
        )
        subparsers = parser.add_subparsers(dest='command',
                                           title='Command used to perform actions in ASM.',
                                           description='Commands that must be the first parameter at "%(prog)s"')

        parent_group = parser.add_argument_group(title='Parameters')
        parent_group.add_argument('--version', '-v',
                                  action='version',
                                  help='ASM CLI version',
                                  version='asm-cli {}, asm-api {}'.format(asm_cli_version, asm_api_version))
        parent_group.add_argument('--help', '-h', action='help', help='Show help')

        upload_parser = subparsers.add_parser('upload', help="Upload package files used for service installation purposes")
        arg_main(sub=upload_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        upload_parser.add_argument('-f', '--file', type=str, nargs='+',
                                   help='The path to the file to be uploaded to ASM (e.g. "C:\\Alphaopen\\alphaopen-adapter-apda-1.9.0.0307-win32.zip")', metavar='[path]')

        download_parser = subparsers.add_parser('download', help="Download package files from network used for service installation purposes")
        arg_main(sub=download_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        download_parser.add_argument('-u', '--url', type=str, nargs='+',
                                     help='The URL of the file to be uploaded to ASM', metavar='[url]', required=True)
        download_parser.add_argument('-a', '--auth', type=str, nargs='?',
                                     help='HTTP basic authentication', metavar='login:password')

        install_parser = subparsers.add_parser('install', help="Install service instance")
        arg_main(sub=install_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        install_parser.add_argument('-p', '--package', type=str, nargs='+',
                                    help='Package name for installation to ASM', metavar='[filename]')

        delete_parser = subparsers.add_parser('delete', help="Delete ASM packages or service instances")
        arg_main(sub=delete_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        delete_parser.add_argument('-c', '--component', type=str, nargs='+',
                     help='ASM service instance name (e.g. adapter_1/alphaopen-adapter-apda-1.9.0.0307-win32.zip)', metavar='[component]')

        rules_parser = subparsers.add_parser('rules', help="Get/Set monitoring rules for your service instances, the Service Manager processes and the operating system")
        arg_main(sub=rules_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        rules_group = rules_parser.add_mutually_exclusive_group()
        rules_group.add_argument('-s', '--set', type=str,
                                help='Set monitoring rules (e.g. "C:\\documents\\script.py")', metavar='[path]')
        rules_group.add_argument('-g', '--get', action='store_true', help='View Monitoring Rules')
        rules_group.add_argument('-e', '--enable', action='store_true', help='Enable Monitoring Rules')
        rules_group.add_argument('-d', '--disable', action='store_true', help='Disable Monitoring Rules')

        conf_parser = subparsers.add_parser('conf', help="Specifying ASM settings")
        arg_main(sub=conf_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        conf_parser.add_argument('-k', '--key', type=str,
                                help='ASM configuration key (e.g. "asm_id")', metavar='[key]', required=True)
        conf_parser.add_argument('-v', '--value', type=str,
                                help='ASM configuration value (e.g. "true")', metavar='[value]', required=True)

        task_parser = subparsers.add_parser('task', help="Set/Get ASM task settings")
        arg_main(sub=task_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        task_parser.add_argument('-c', '--component', type=str, nargs='+',
                                help='ASM service instance name (e.g. "server_1"). If not specified returns all ASM service instances.', metavar='[component_id]')
        task_parser.add_argument('-k', '--key', type=str,
                                help='ASM service instance configuration key (e.g. "alias"). If not specified returns full tree.', metavar='[key]')
        task_parser.add_argument('-v', '--value', type=str,
                                help='ASM service instance configuration value (e.g. "test_server"). If not specified returns -k/--key value.', metavar='[value]')

        set_parser = subparsers.add_parser('set', help="Set ASM service instance settings")
        arg_main(sub=set_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        arg_component(sub=set_parser)
        set_parser.add_argument('-k', '--key', type=str,
                                help='Component configuration key (e.g. "address / conf\\acs.xml")', metavar='[key]')
        set_parser.add_argument('-v', '--value', type=str,
                                help='Component configuration value (e.g. "0.0.0.0 / acs.xml")', metavar='[value]')

        alias_parser = subparsers.add_parser('alias', help="Set ASM service instance alias")
        arg_main(sub=alias_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        alias_parser.add_argument('-c', '--component', type=str,
                     help='ASM service instance name (e.g. "server_1")', metavar='[component_id]', required=True)
        alias_parser.add_argument('-a', '--alias', type=str,
                                help='ASM service instance alias (e.g. "test_server")', metavar='[alias]', default=None)

        get_parser = subparsers.add_parser('get', help="Get ASM users/conf/task/files")
        arg_main(sub=get_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        get_parser.add_argument('-c', '--component', type=str, nargs='+',
                     help='ASM service instance name (e.g. "adapter_1" / "users" / "task" / "files" / "conf" / "export")', metavar='[component]')
        get_parser.add_argument('-p', '--property', type=str, nargs='+',
                     help='ASM service instance property (e.g. "port" / "conf\\acs.xml" / "adaper")', metavar='[property]')

        log_parser = subparsers.add_parser('log', help="Download log files for ASM service instances")
        arg_main(sub=log_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        arg_component(sub=log_parser)
        log_parser.add_argument('-p', '--path', type=str,
                                help='Path to save file (e.g. "C:/downloads/")', default=".")

        info_parser = subparsers.add_parser('info', help="Provides information about operational system and resources")
        arg_main(sub=info_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        info_parser.add_argument('-p', '--property', type=str, nargs='+',
                     help='ASM info property (e.g. "os_name")', metavar='[property]', default=['all'])

        process_parser = subparsers.add_parser('process', help="Provides information about operational system processes")
        arg_main(sub=process_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        process_parser.add_argument('-k', '--key', type=str,
                    help='Key to sort ASM processes (e.g. "name")', metavar='[key]')
        process_parser.add_argument('-v', '--value', type=str,
                    help='Value to sort ASM processes (e.g. "python.exe")', metavar='[value]')
        process_parser.add_argument('-p', '--property', type=str, nargs='?',
                    help='ASM process info property (e.g. "pid")', metavar='[property]', default='all')

        start_parser = subparsers.add_parser('start', help="Start ASM service instance")
        arg_main(sub=start_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        start_parser.add_argument('-c', '--component', type=str, nargs='+',
                     help='ASM service instance (e.g. "adapter_1" / "adapter" / "all")', metavar='[component]')

        stop_parser = subparsers.add_parser('stop', help="Stop ASM service instance")
        arg_main(sub=stop_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        stop_parser.add_argument('-c', '--component', type=str, nargs='+',
                     help='ASM service instance (e.g. "adapter_1" / "adapter" / "all")', metavar='[component]')

        restart_parser = subparsers.add_parser('restart', help="Restart ASM service instance")
        arg_main(sub=restart_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        restart_parser.add_argument('-c', '--component', type=str, nargs='+',
                     help='ASM service instance (e.g. "adapter_1" / "adapter" / "all")', metavar='[component]')

        script_parser = subparsers.add_parser('script', help="Create script for ASM service instance")
        arg_main(sub=script_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        arg_component(sub=script_parser)

        kill_parser = subparsers.add_parser('kill', help="Kill process by pid")
        arg_main(sub=kill_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        kill_parser.add_argument('-p', '--pid', type=str, nargs='?',
                     help='Process pid (e.g. "3423")', metavar='[pid]')

        lib_parser = subparsers.add_parser('lib', help="Adding, viewing and updating dependency libraries for ASM")
        arg_main(sub=lib_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        lib_group = lib_parser.add_mutually_exclusive_group()
        lib_group.add_argument('-u', '--upload', type=str, nargs='*',
                    help='Lib archive for upload (e.g. "alphalogic_api-0.0.14.zip")', metavar='[lib]')
        lib_group.add_argument('-f', '--files', type=str, nargs='*',
                    help='Get ASM Lib packages', metavar='[lib]')
        lib_group.add_argument('-l', '--list', action='store_true',
                    help='Get ASM library list')
        lib_group.add_argument('-v', '--version', type=str, nargs='*',
                    help='Get ASM library version', metavar='[lib]')
        lib_group.add_argument('-i', '--install', type=str, nargs='+',
                    help='Package to install or update (e.g. "alphalogic_api-0.0.14.zip")', metavar='[lib]')
        lib_group.add_argument('--freeze', action='store_true',
                    help='Output installed packages in requirements format.')

        cert_parser = subparsers.add_parser('cert', help="Adding, viewing, removing and downloading ASM certificates and truststore")
        arg_main(sub=cert_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        cert_group = cert_parser.add_mutually_exclusive_group()
        cert_group.add_argument('-u', '--upload', type=str, nargs='*',
                    help='Certificate for upload (e.g. "service.crt")', metavar='[crt]')
        cert_group.add_argument('-d', '--download', type=str,
                    help='Download ASM certificate (e.g. "C:/downloads" / "C:/downloads/service.crt")', metavar='[path]')
        cert_group.add_argument('-s', '--truststore', type=str,
                    help='Download ASM truststore (e.g. "C:/downloads")', metavar='[path]')
        cert_group.add_argument('-r', '--remove', type=str, nargs='*',
                    help='Remove certificate by alias (e.g. "alpha-1544696037")', metavar='[alias]')
        cert_group.add_argument('-i', '--info', action='store_true',
                    help='View Trusted Certificates information')
        cert_group.add_argument('-l', '--list', action='store_true',
                    help='List of Trusted Certificates')


        # xml_parser = subparsers.add_parser('xml', help="Edit ASM file")
        # arg_main(sub=xml_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        # arg_component(sub=xml_parser)
        # xml_parser.add_argument('-f', '--file', type=str,
        #                         help='ASM service instance file (e.g. "conf/acs.xml")', metavar='[file]')
        # xml_parser.add_argument('-v', '--value', type=str,
        #                         help='Value to write', metavar='[value]')

        # user_parser = subparsers.add_parser('user')
        # arg_main(sub=user_parser, default_host=dh, default_port=dp, default_token=dt, default_timeout=dtm)
        # user_parser.add_argument('-a', '--action', type=str, choices=('add','delete'),
        #                              help='Action to do (e.g. add/delete)')
        # user_parser.add_argument('-u', '--username', type=str, nargs='+',
        #                         help = 'ASM user username (e.g. "user1")')
        # user_parser.add_argument('-e', '--email', type=str,
        #                              help='ASM user email (e.g. "user@gmail.com")')
        # user_parser.add_argument('-p', '--userpassword', type=str,
        #                              help='ASM user password (e.g. "user1")')
        # user_parser.add_argument('-s', '--staff', type=str, choices=('true', 'false'), default='false',
        #                              help='ASM user type (e.g. admin - "true", user - "false")')
        # user_parser.add_argument('--id', type=str, nargs='+',
        #                          help='ASM user type (e.g. admin - "true", user - "false")')

        return parser
