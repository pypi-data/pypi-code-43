__all__ = [
    'parse_args',
    'sphinx_config',
]

import argparse
import os
from subprocess import check_call

from . import sphinx_config

SOURCE_DIR = '.'
BUILD_DIR = 'build'


def parse_args():
    known_commands = {
        'clean': clean_docs,
        'build': build_docs,
        'check': check_docs,
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


def _sphinx_build(cmd, source_dir, allow_warnings):
    cmd = ['sphinx-build', '-M', cmd, SOURCE_DIR, BUILD_DIR]
    if not allow_warnings:
        cmd += ['-W']
    return check_call(cmd, cwd=source_dir)
