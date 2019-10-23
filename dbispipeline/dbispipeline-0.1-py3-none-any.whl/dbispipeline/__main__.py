"""Declaring the main method of this package."""
import argparse

import git

from .core import Core
from .output_handlers import PostGresOutputHandler, PrintHandler
import logging
from .utils import LOGGER
from .utils import restore_backup

parser = argparse.ArgumentParser(description="executes dbis config files")
# TODO: configurationfile is required but it is i.e. not needed for restore
parser.add_argument('configurationfile', help='file that holds config')
parser.add_argument(
    '-f', '--force', action='store_true', help="Run with dirty git")
parser.add_argument(
    '--dryrun',
    action='store_true',
    help='run without sending results to database.')
parser.add_argument(
    '--path',
    default=None,
    type=str,
    help="Path used as that can be used as prefix for file paths.")
parser.add_argument(
    '-m',
    '--mail',
    choices=[None, 'run', 'total'],
    default=None,
    help='Mail notification level. Choose one of [None, \'run\', \'total\''
    ']. If set no None, no mails will be sent. if set to \'run\', one info'
    ' mail will be sent for each run. If set to \'total\', one mail will '
    'be sent after the entire pipeline is complete.')
parser.add_argument(
    '--restore',
    default=None,
    type=str,
    help="Restores the backup contained in the given file.")
parser.add_argument(
    '-v', '--verbose', action='store_true', help='increase logging')
args = parser.parse_args()


def main():
    """Entry point that executes the pipeline given a configuration."""

    if args.verbose:
        LOGGER.setLevel(logging.DEBUG)
        LOGGER.debug('setting logging level to DEBUG')

    if args.restore:
        restore_backup(args.restore, [PrintHandler(), PostGresOutputHandler()])
        exit(0)

    if not args.force:
        try:
            repo = git.Repo(search_parent_directories=True)
            if repo.is_dirty():
                LOGGER.error(
                    "Please commit your changes before you run the pileline.")
                exit(1)
        except git.GitError:
            pass

    Core(
        args.configurationfile,
        path_prefix=args.path,
        dryrun=args.dryrun,
        mail=args.mail).run()


if __name__ == '__main__':
    main()
