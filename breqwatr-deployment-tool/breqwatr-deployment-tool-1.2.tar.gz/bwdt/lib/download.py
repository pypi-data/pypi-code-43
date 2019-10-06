""" Commands for downloading from s3 """
import os
import sys

import click

from bwdt.lib.aws.s3 import S3
from bwdt.constants import (APT_TARGZ_KEY, BWDT_TARGZ_KEY, CLOUDYML_KEY,
                            S3_BUCKET)


def _save(path, key, force):
    """ Download the specified file """
    files_dir = '{}/{}'.format(path, 'files')
    if os.path.isdir(path):
        full_path = '{}/{}'.format(files_dir, key)
    else:
        err = 'ERROR: path {} must be a directory and exist\n'.format(path)
        sys.stderr.write(err)
        return False
    if not os.path.exists(files_dir):
        os.mkdir(files_dir)
    if os.path.exists(full_path) and not force:
        err = 'WARN: File {} exists. Use --force to replace'.format(full_path)
        click.echo(err)
        return False
    click.echo('Saving {}'.format(full_path))
    full_path = '{}/{}'.format(files_dir, key)
    S3().download(full_path, S3_BUCKET, key)
    return True


def offline_apt(path, force):
    """ Download a subset of breqwatr/apt for offline installs """
    _save(path, APT_TARGZ_KEY, force)


def offline_bwdt(path, force):
    """ Download an offline export of this bwdt tool """
    _save(path, BWDT_TARGZ_KEY, force)


def cloud_yml(path, force):
    """ Download a commented cloud.yml template """
    _save(path, CLOUDYML_KEY, force)
