import os
import sys
import click
import glob
import logging
from os.path import join
from collections import defaultdict, Counter
import json
import yaml

from mcutk.projects_scanner import find_projects
from mcutk.managers.conf_mgr import ConfMgr


SDK_TYPES = [
    'driver_examples',
    'demo_apps',
    'multicore_examples',
    'wireless_examples',
    'aws_examples',
    'cmsis_driver_examples',
    'trustzone_examples',
    'usb_examples',
    'wifi_qca_examples',
]


def get_app_type(path):
    path = os.path.abspath(path).replace('\\', '/')
    parts = path.split('/')



@click.command('scan', short_help='projects scanner')
@click.argument('path', required=True, type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(exists=False), help='dump scan results to file, file format support: json or yml.')
@click.option('--dapeng', is_flag=True, default=False, help='dump for dapeng style, casfile.yml')
def cli(path, output, dapeng):
    projects, count = find_projects(path, True)
    dataset = list()

    if output:
        extension = os.path.basename(output).split(".")[-1]
        for tname, plist in projects.items():
            for project in plist:
                dataset.append(project.to_dict())

        if extension in ('yml', 'yaml'):
            with open(output, 'w') as file:
                yaml.safe_dump(dataset, file, default_flow_style=False)
        else:
            with open(output, 'w') as file:
                json.dump(dataset, file)

        # elif format == 'dapeng':
        #     for project in projects:
        #         if project.path
        # else:
        #     pass

        click.echo("output file: %s"%output)




