#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
file name: package_generator.py
author: Shlomi Ben-David (shlomi.ben.david@gmail.com)
file version: 0.0.1
description: The package_generator is tool that used to generate
    the python packages.
The user must supply the following required arguments:
- package_name
- author
- author_email
The user can supply the following optional arguments
- url to package content on github.com or gitlab.com
- version_file
- python_version (i.e 3.5)
- description
"""
import os
import sys
import logging
from shutil import copytree
from pylib3 import init_logging
from string import Template
from glob import glob
from pygenerator3.args import get_cli_args

logger = logging.getLogger(__name__)
BASE_PATH = os.path.dirname(__file__)
TEMPLATES_DIR = os.path.join(BASE_PATH, 'templates')


def handle_package_dir(src_path, dst_path, **items):
    """
    Handles package directory

    :param str src_path: source directory path
    :param str dst_path: destination directory path
    """
    dir_name = os.path.basename(src_path)
    if dir_name != 'package':
        return

    logger.debug("src_path: {}".format(src_path))
    logger.debug("dst_path: {}".format(dst_path))
    try:
        copytree(src=src_path, dst=dst_path)
        logger.info(
            "Copying '{}' directory to '{}'"
            .format(src_path, dst_path)
        )
    except FileExistsError:
        pass

    # create <package_name>_VERSION file
    version_file_path = os.path.join(dst_path, items['version_file'])
    package_version = items['package_version']
    logger.info(
        "Creating '{}' file and updating it's version to {}"
        .format(version_file_path, package_version)
    )
    with open(version_file_path, 'w') as ofile:
        ofile.write(package_version)


def handle_template_file(src_path, dst_path, **items):
    """
    Handle template file

    :param src_path: source file path
    :param dst_path: destination file path
    """
    logger.debug(">" * 80)
    file_name = os.path.basename(src_path).replace('.template', '')

    logger.debug("Reading from '{}' file".format(src_path))
    with open(src_path) as ifile:
        data = ifile.read()

    s = Template(data)
    new_data = s.safe_substitute(**items)
    logger.info("Updating '{}' file content".format(file_name))

    dst_file_path = os.path.join(dst_path, file_name)
    try:
        logger.debug("Writing to '{}' file".format(dst_file_path))
        with open(dst_file_path, 'w') as ofile:
            ofile.write(new_data)
    except PermissionError as err:
        logger.error(err)

    logger.debug("<" * 80)


def main():
    """ MAIN """

    # get commandline arguments
    args = get_cli_args()

    # init logger
    init_logging(
        log_file=args.log_file,
        console=args.console,
        verbose=args.verbose
    )

    package_name = args.package_name
    version_file = \
        args.version_file or "{}_VERSION".format(package_name.upper())
    dst_path = args.dst or os.path.realpath('.')

    logger.info("Generating package structure")

    # create package primary directory
    primary_dir_path = os.path.join(dst_path, package_name)
    if not os.path.exists(primary_dir_path):
        logger.info("Creating '{}' directory".format(primary_dir_path))
        os.mkdir(primary_dir_path)

    logger.info("Collecting template files")
    template_files = glob(TEMPLATES_DIR + '/.*') + glob(TEMPLATES_DIR + '/*')
    logger.debug("template files: {}".format(template_files))

    items = {
        'package_name': package_name,
        'author': args.author,
        'author_email': args.author_email,
        'description': args.description,
        'url': args.url,
        'version_file': version_file,
        'python_version': args.python_version,
        'package_version': args.package_version
    }

    for temp_path in template_files:
        if os.path.isdir(temp_path):
            dst_package_path = os.path.join(primary_dir_path, package_name)
            handle_package_dir(
                src_path=temp_path, dst_path=dst_package_path, **items
            )
            continue

        handle_template_file(
            src_path=temp_path, dst_path=primary_dir_path, **items
        )

    logger.info("Package '{}' successfully created".format(package_name))


if __name__ == '__main__':
    sys.exit(main())
