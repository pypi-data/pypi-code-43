import argparse
import textwrap

import logging
from functools import partial

from package_uploader.log_utils import setup_cli_output
from package_uploader.conf import setup, settings
from package_uploader.exceptions import GenericError
from package_uploader import upload_package


def main():
    setup_cli_output()
    setup()

    parser = argparse.ArgumentParser(
        description=textwrap.dedent("""
            Python Package Uploader.
            This script uploads any python package into supported artifacts repositories (self-hosted pypi, gitlab, github,
            bitbucket...). 
        """).strip(),
        formatter_class=partial(argparse.HelpFormatter, width=120, max_help_position=32),
    )
    parser.add_argument(
        'repository',
        help="destination repository", choices=list(settings.repositories.keys())
    )
    parser.add_argument(
        'versions',
        nargs="*", help="version to be uploaded (default: current package version from setup.py)",
        default=[], metavar='version'
    )
    parser.add_argument(
        '--skip-empty-versions',
        help="skip versions that don't have candidates for upload instead of failing.",
        dest="skip_empty_versions", action='store_true'
    )
    # parser.add_argument(
    #     '-p', '--package',
    #     help="path to the package source directory (containing setup.py) (default: current dir)",
    #     metavar="path"
    # )

    args = parser.parse_args()

    repository = settings.get_repository(args.repository)
    try:
        upload_package(repository=repository, versions=args.versions, skip_empty_versions=args.skip_empty_versions)
    except GenericError as e:
        logging.error(*e.args)
        exit(1)


if __name__ == '__main__':
    main()
