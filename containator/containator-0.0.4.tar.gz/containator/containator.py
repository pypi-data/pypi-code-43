#!/usr/bin/env python3

import os
import json
import argparse
import traceback
import subprocess
from configparser import ConfigParser
from pprint import pprint

import docker
import docker.utils

from .defs import *
from .volume import VolumeGroup
from .utils import getfirst

class Containator(object):
    def run_cli(self):
        self.parse_args()
        self.read_config(self.args.container, self.args.config)
        self.attach = getfirst(self.args.attach, self.conf.getboolean('attach'))
        self.logs = getfirst(self.args.logs, self.conf.getboolean('logs'))
        self.wait = getfirst(self.args.wait, self.conf.getboolean('wait'))
        self.remove = getfirst(self.args.remove, self.conf.getboolean('remove'))
        self.start(self.args.container)

    def start(self, container):
        if self.attach:
            import dockerpty
        
        self.client = docker.Client()
        
        create_args = {}
        create_args['image'] = self.conf['image']
        create_args['host_config'] = self.client.create_host_config()
        if self.conf.getboolean('named'):
            create_args['name'] = self.conf['name'] if self.conf.get('name') else container
        
        if self.attach:
            create_args['stdin_open'] = True
            create_args['tty'] = True
        
        volumes = VolumeGroup(self.conf.get('volumes'))
        if volumes:
            create_args['volumes'] = volumes.guest_path_list()
            create_args['host_config']['binds'] = volumes.volume_def_list()
        
        if self.conf.get('extra_params'):
            create_args.update(json.loads(self.conf['extra_params']))
        
        container = self.client.create_container(**create_args)
        self.client.start(container)
        container_info = self.client.inspect_container(container)
        
        if self.args.debug:
            pprint(container_info)
        
        if self.conf.get('cmd_after'):
            try:
                subprocess.check_call(self.conf['cmd_after'].format(**container_info), shell=True)
            except:
                traceback.print_exc()
        
        if self.attach:
            dockerpty.start(self.client, container)
        elif self.logs:
            print('container output:')
            output = self.client.attach(container, stdout=True, stderr=True, stream=True, logs=True)
            try:
                for line in output:
                    print(line.decode('utf-8'), end='')
            except KeyboardInterrupt:
                pass
        elif self.wait or self.remove:
            print('waiting for container to finish...')
            try:
                self.client.wait(container)
            except KeyboardInterrupt:
                pass
        if self.remove:
            print('removing container')
            self.client.remove_container(container, v=True, force=True)

    def parse_args(self, args=None):
        parser = argparse.ArgumentParser(description=app_name_desc)
        parser.add_argument('-V', '--version', action='version', version=app_version,
                help='print version information')
        parser.add_argument('-c', '--config',
                help='config file (default: {})'.format(', '.join(CONFIG_FILES)))
        parser.add_argument('-d', '--debug', action='store_true')
        g = parser.add_mutually_exclusive_group()
        g.add_argument('--attach', action='store_true', default=None,
                help='attach a pty')
        g.add_argument('--no-attach', dest='attach', action='store_false',
                help='overrides "attach" from config file')
        g = parser.add_mutually_exclusive_group()
        g.add_argument('--logs', action='store_true', default=None,
                help='stream output from container')
        g.add_argument('--no-logs', dest='logs', action='store_false')
        g = parser.add_mutually_exclusive_group()
        g.add_argument('--wait', action='store_true', default=None,
                help='wait for container to finish')
        g.add_argument('--no-wait', dest='wait', action='store_false')
        g = parser.add_mutually_exclusive_group()
        g.add_argument('--remove', action='store_true', default=None,
                help='remove container when finished (implies wait)')
        g.add_argument('--no-remove', dest='wait', action='store_false')
        parser.add_argument('container', help='container from config file')
        self.args = parser.parse_args(args=args)

    def read_config(self, container, configfile=None):
        conf = ConfigParser()
        if configfile is not None:
            with open(configfile, 'r') as f:
                conf.readfp(f)
        else:
            if not conf.read(os.path.expanduser(x) for x in CONFIG_FILES):
                raise RuntimeError('Unable to read any default config file.')
        self.conf = conf[container]

