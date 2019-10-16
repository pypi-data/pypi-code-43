__all__ = [
    'parse_args',
    'sphinx_config',
]

import argparse
import os
from os.path import join
import shutil
from subprocess import check_call, check_output

from . import sphinx_config

SOURCE_DIR = '.'
BUILD_DIR = 'build'


def parse_args():
    known_commands = {
        'clean': clean_docs,
        'build': build_docs,
        'check': check_docs,
        'deploy': deploy_docs,
    }

    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=known_commands)
    parser.add_argument('--source-dir', required=False, default=os.getcwd())
    parser.add_argument('--allow-warnings', action='store_true')

    args = parser.parse_args()

    known_commands[args.command](
        source_dir=args.source_dir,
        allow_warnings=args.allow_warnings
    )


def clean_docs(source_dir, allow_warnings=False):
    _sphinx_build('clean', source_dir, allow_warnings)


def build_docs(source_dir, allow_warnings=False):
    _sphinx_build('html', source_dir, allow_warnings)


def check_docs(source_dir, allow_warnings=False):
    _sphinx_build('linkcheck', source_dir, allow_warnings)


def deploy_docs(source_dir, allow_warnings=False):
    if os.environ['TRAVIS_BRANCH'] != 'master':
        print('This commit was made against', os.environ['TRAVIS_BRANCH'],
              'and not the master! No deploy!')
        return

    built_dir = join(source_dir, BUILD_DIR, 'html')
    git_rev = check_output(['git', 'rev-parse', '--short', 'HEAD'],
                           cwd=source_dir, universal_newlines=True)
    shutil.copy(join(source_dir, SOURCE_DIR, '.nojekyll'), built_dir)

    check_call(['git', 'init'], cwd=built_dir)
    check_call(['git', 'config', 'user.name', 'Alex Pearce'], cwd=built_dir)
    check_call(['git', 'config', 'user.email', 'alex@alexpearce.me'], cwd=built_dir)

    push_url = 'https://' + os.environ['GH_TOKEN'] + '@github.com/lhcb/starterkit-lessons.git'
    check_call(['git', 'remote', 'add', 'upstream', push_url], cwd=built_dir)
    check_call(['git', 'fetch', 'upstream'], cwd=built_dir)
    check_call(['git', 'reset', 'upstream/gh-pages'], cwd=built_dir)

    check_call(['touch', '.'], cwd=built_dir)

    check_call(['git', 'add', '-A', '.'], cwd=built_dir)
    check_call(['git', 'commit', '-m', 'Rebuild pages at ' + git_rev], cwd=built_dir)
    check_call(['git', 'push', '-q', 'upstream', 'HEAD:gh-pages'], cwd=built_dir)


def _sphinx_build(cmd, source_dir, allow_warnings):
    cmd = ['sphinx-build', '-M', cmd, SOURCE_DIR, BUILD_DIR]
    if not allow_warnings:
        cmd += ['-W']
    return check_call(cmd, cwd=source_dir)
