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
    check_call(['sphinx-build', '-M', 'clean', SOURCE_DIR, BUILD_DIR, '-W'], cwd=source_dir)


def build_docs(source_dir, allow_warnings=False):
    check_call(['sphinx-build', '-M', 'html', SOURCE_DIR, BUILD_DIR, '-W'], cwd=source_dir)


def check_docs(source_dir, allow_warnings=False):
    check_call(['sphinx-build', '-M', 'linkcheck', SOURCE_DIR, BUILD_DIR, '-W'], cwd=source_dir)
