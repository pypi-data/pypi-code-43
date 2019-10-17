"""
CLI commands for docker actions
"""


import json
from os import makedirs, path
from subprocess import check_call

import click

from brewblox_deploy.utils import confirm

WORKDIR = path.expanduser('~/.cache/bbdeploy/docker')

PYTHON_TAGS = [
    '3.7', '3.7-slim',
    '3.8', '3.8-slim',
]
NODE_TAGS = [
    '10', '10-slim',
    '11', '11-slim',
]

AMD_ARM_REPOS = [
    'brewblox/brewblox-ctl-lib',
    'brewblox/brewblox-devcon-spark',
    'brewblox/brewblox-history',
    'brewblox/brewblox-mdns',
    'brewblox/brewblox-ui',
    'brewblox/firmware-flasher',
]
AMD_REPOS = [
    'brewblox/firmware-simulator',
]


@click.group()
def cli():
    """Collection group"""


def enable_experimental():
    fname = path.expanduser('~/.docker/config.json')
    try:
        with open(fname, 'r') as f:
            content = f.read()
            config = json.loads(content or '{}')
    except FileNotFoundError:
        config = {}

    if 'experimental' in config.keys():
        return

    with open(fname, 'w') as f:
        config['experimental'] = 'enabled'
        json.dump(config, f, indent=4)


def install_qemu():
    check_call('sudo apt update', shell=True)
    check_call('sudo apt install -y qemu qemu-user-static qemu-user binfmt-support', shell=True)
    check_call(f'cp $(which qemu-arm-static) {WORKDIR}/', shell=True)


def build_python_images():
    for tag in PYTHON_TAGS:
        with open(f'{WORKDIR}/Dockerfile', 'w') as f:
            f.write('\n'.join([
                f'FROM arm32v7/python:{tag}',
                'COPY ./qemu-arm-static /usr/bin/qemu-arm-static',
            ]))
        check_call(f'docker pull --platform=linux/arm arm32v7/python:{tag}', shell=True)
        check_call(f'docker build --platform=linux/arm --no-cache -t brewblox/rpi-python:{tag} {WORKDIR}', shell=True)
        check_call(f'docker push brewblox/rpi-python:{tag}', shell=True)


def build_node_images():
    for tag in NODE_TAGS:
        with open(f'{WORKDIR}/Dockerfile', 'w') as f:
            f.write('\n'.join([
                f'FROM arm32v7/node:{tag}',
                'COPY ./qemu-arm-static /usr/bin/qemu-arm-static',
            ]))
        check_call(f'docker pull --platform=linux/arm arm32v7/node:{tag}', shell=True)
        check_call(f'docker build --platform=linux/arm --no-cache -t brewblox/rpi-node:{tag} {WORKDIR}', shell=True)
        check_call(f'docker push brewblox/rpi-node:{tag}', shell=True)

    # Alpine is an exception, as it runs on armv6, and must install packages
    with open(f'{WORKDIR}/Dockerfile', 'w') as f:
        f.write('\n'.join([
            'FROM arm32v6/alpine',
            'COPY ./qemu-arm-static /usr/bin/qemu-arm-static',
            'RUN apk add --no-cache nodejs npm',
        ]))

    check_call('docker pull --platform=linux/arm arm32v6/alpine', shell=True)
    check_call(f'docker build --platform=linux/arm --no-cache -t brewblox/rpi-node:10-alpine {WORKDIR}', shell=True)
    check_call('docker push brewblox/rpi-node:10-alpine', shell=True)


@cli.command()
def docker_info():
    print(f'Stash directory:', WORKDIR)
    print('Python tags', *PYTHON_TAGS, sep='\n\t')
    print('Node tags', *NODE_TAGS, sep='\n\t')
    print('AMD+ARM repositories:', *AMD_ARM_REPOS, sep='\n\t')
    print('AMD repositories:', *AMD_REPOS, sep='\n\t')


@cli.command()
def docker_images():
    makedirs(WORKDIR, exist_ok=True)
    enable_experimental()
    install_qemu()

    if confirm('Do you want to build and push Python base images?'):
        build_python_images()

    if confirm('Do you want to build and push Node base images?'):
        build_node_images()


@cli.command()
def release_stable():
    for repo in AMD_ARM_REPOS + AMD_REPOS:
        check_call(f'docker pull {repo}:newest-tag', shell=True)

    for repo in AMD_ARM_REPOS:
        check_call(f'docker pull {repo}:rpi-newest-tag', shell=True)

    # start pushing after all pulls are ok

    for repo in AMD_ARM_REPOS + AMD_REPOS:
        check_call(f'docker tag {repo}:newest-tag {repo}:stable', shell=True)
        check_call(f'docker push {repo}:stable', shell=True)

    for repo in AMD_ARM_REPOS:
        check_call(f'docker tag {repo}:rpi-newest-tag {repo}:rpi-stable', shell=True)
        check_call(f'docker push {repo}:rpi-stable', shell=True)
