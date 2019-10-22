import argparse
import sys

from pydist_cli.install import install
from pydist_cli.settings import load_settings
from pydist_cli.publish import publish


base_parser = argparse.ArgumentParser(description='Build, upload and download python packages.')
base_parser.add_argument('command', choices=['install', 'publish'])
base_parser.add_argument('--api-key')
base_parser.add_argument('--tag', help='Tag downloads to disambiguate them in pydist.com/insights.')
base_parser.add_argument('--index', help='Package index to use.')
base_parser.add_argument('--backup-index', help='Backup index to install packages from, if primary is unreachable.')
base_parser.add_argument('--public', action='store_true', help='Use PyPI instead of PyDist (overrides --index).')
base_parser.add_argument('--username', help='Username for uploading to PyPI.')
base_parser.add_argument('args', nargs=argparse.REMAINDER, help='(varies by command)')


def _main(*args):
    base_args = base_parser.parse_args(args)
    command = base_args.command
    args = base_args.args
    settings = load_settings(base_args)

    if command == 'install':
        install(settings, args)
    elif command == 'publish':
        publish(settings)


def main():
    _main(*sys.argv[1:])
