"""
Commands for git operations
"""

from contextlib import suppress
from os import makedirs, path
from shutil import which
from subprocess import CalledProcessError, check_call, check_output

import click
from brewblox_deploy.utils import confirm

HUB_VERSION = '2.10.0'
WORKDIR = path.expanduser('~/.cache/bbdeploy/git')
REPOS = [
    'brewblox-devcon-spark',
    'brewblox-history',
    'brewblox-mdns',
    'brewblox-ui',
    'brewblox-ctl-lib',
    'brewblox-web-editor',
    'brewblox-firmware',
    'brewblox-plaato',
]


@click.group()
def cli():
    """Command collector"""


def create_repos():
    makedirs(WORKDIR, exist_ok=True)
    [
        check_output(
            f'git clone --no-checkout https://github.com/BrewBlox/{repo}.git', shell=True, cwd=WORKDIR)
        for repo in REPOS
        if not path.exists(f'{WORKDIR}/{repo}/.git')
    ]


def install_hub():
    [
        check_output(cmd, shell=True)
        for cmd in [
            f'wget https://github.com/github/hub/releases/download/v{HUB_VERSION}/hub-linux-amd64-{HUB_VERSION}.tgz',
            f'tar zvxvf hub-linux-amd64-{HUB_VERSION}.tgz',
            f'sudo ./hub-linux-amd64-{HUB_VERSION}/install',
            f'rm -rf hub-linux-amd64-{HUB_VERSION}*',
        ]
    ]


def prepare():
    create_repos()
    if not which('hub') and confirm('hub cli not found - do you want to install it?'):
        install_hub()


@cli.command()
def git_info():
    print('Stash directory:', WORKDIR)
    print('Github repositories:', *REPOS, sep='\n\t')
    check_call('hub --version', shell=True)


@cli.command()
def delta():
    prepare()

    headers = ['repository'.ljust(25), 'develop >', 'edge >', 'tag']
    print(*headers)
    # will include separators added by print()
    print('-' * len(' '.join(headers)))
    for repo in REPOS:
        check_output('git fetch --tags --quiet',
                     shell=True,
                     cwd=f'{WORKDIR}/{repo}')
        dev_edge = check_output(
            'git rev-list --count origin/edge..origin/develop',
            shell=True,
            cwd=f'{WORKDIR}/{repo}').decode().rstrip()
        edge_tag = check_output(
            'git rev-list --count $(git rev-list --tags --max-count=1)..origin/edge',
            shell=True,
            cwd=f'{WORKDIR}/{repo}').decode().rstrip()
        vals = [repo, dev_edge, edge_tag, '-']
        print(*[v.ljust(len(headers[idx])) for idx, v in enumerate(vals)])


@cli.command()
def release_edge():
    prepare()

    for repo in REPOS:
        if not confirm(f'Do you want to create a develop -> edge PR for {repo}?'):
            continue

        with suppress(CalledProcessError):
            check_call(
                'hub pull-request -b edge -h develop -m "edge release"',
                shell=True,
                cwd=f'{WORKDIR}/{repo}')
