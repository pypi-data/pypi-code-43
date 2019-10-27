#!/usr/bin/env python
#
# Copyright 2018-2019 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#
# This utility downloads one or more files from an existing bucket in
# a Cloud Object Storage instance on IBM Cloud.
#


import argparse
import os
import re
import sys

from pathlib import Path

from .cos import COSWrapper, COSWrapperError


class DownloadError(Exception):
    pass


def do_download(bucket,
                source_spec,
                access_key_id,
                secret_access_key,
                target_dir='.',
                verbose=False):
    """
    Download the objects(s) identified by source_spec
    from the specified Cloud Object Storage bucket to
    target_dir.

    :param bucket: Source bucket name. (Must exist)
    :type bucket: str
    :param source_spec: Identifies an object or multiple objects
    in bucket.
    :type source_spec: str
    :param access_key_id: HMAC access key id
    :type access_key_id: str
    :param secret_access_key: HMAC secret access key
    :type secret_access_key: str
    :param target_dir: Directory where objects shall be stored. This
    directory must exist and be writable. Defaults to the current directory.
    :type target_dir: str, optional
    :raises ValueError: A required parameter value is missing.
    :raises DownloadError: Download failed due to the specified reason.
    :return: number of downloaded objects
    :rtype: int
    """

    if not bucket:
        raise ValueError('Parameter "bucket" is required')

    if not source_spec:
        raise ValueError('Parameter "source_spec" is required')

    if not access_key_id:
        raise ValueError('Parameter "access_key_id" is required')

    if not secret_access_key:
        raise ValueError('Parameter "secret_access_key" is required')

    # verify that target_dir is valid
    if not target_dir:
        target_dir = '.'

    if not os.access(target_dir, os.W_OK):
        raise DownloadError('"{}" is not a writable directory'
                            .format(target_dir))

    try:
        # instantiate Cloud Object Storage wrapper
        cw = COSWrapper(access_key_id,
                        secret_access_key)
    except COSWrapperError as cwe:
        raise DownloadError('Cannot access Cloud Object Storage: {}'
                            .format(cwe))

    # fetch list of objects in the bucket
    try:
        objects = cw.get_object_list(bucket)
    except Exception as ex:
        raise DownloadError('Listing of bucket "{}" failed: {}'
                            .format(bucket, ex))

    # sanitize source specification
    pattern = source_spec.replace('.', '\\.')
    pattern = pattern.replace('*', '.*')
    pattern = pattern.replace('?', '.?')
    pattern = '^{}$'.format(pattern)
    # precompile pattern
    prog = re.compile(pattern)

    # download objects matching the source specification
    try:
        object_count = 0

        for object in objects:
            # apply specification to object key
            if not prog.match(object):
                continue

            target = str(Path(target_dir).joinpath(object))

            if verbose:
                print('Downloading "{}" => "{}"'.format(object, target))

            cw.download_object(bucket, object, target)

            object_count = object_count + 1

        if object_count == 0:
            raise DownloadError('No objects in bucket "{}" match the '
                                '"{}" specification.'
                                .format(bucket, source_spec))

        # return number of downloaded files
        return object_count

    except DownloadError:
        # bubble up
        raise
    except Exception as ex:
        # catch and mask exception
        raise DownloadError('Download from bucket "{}" failed: {}'
                            .format(bucket, ex))


def main():

    epilog_msg = 'Environment variables AWS_ACCESS_KEY_ID and ' \
                 'AWS_SECRET_ACCESS_KEY must be defined to run the utility.'

    parser = argparse.ArgumentParser(description='Download objects from a '
                                                 'Cloud Object '
                                                 'Storage bucket.',
                                     epilog=epilog_msg)
    parser.add_argument('bucket',
                        help='Bucket name')
    parser.add_argument('pattern',
                        help='Object key spec (supported wildcards: * and ?)')
    parser.add_argument('-d',
                        '--target_dir',
                        help='Local target directory. '
                             'Defaults to the current directory.')

    # parse command line parameters
    args = parser.parse_args()

    # verify that the required environment variables are set
    # - AWS_ACCESS_KEY_ID
    # - AWS_SECRET_ACCESS_KEY
    if (os.environ.get('AWS_ACCESS_KEY_ID') is None) or \
       (os.environ.get('AWS_SECRET_ACCESS_KEY') is None):
        print('Error. Environment variables AWS_ACCESS_KEY_ID'
              ' and AWS_SECRET_ACCESS_KEY must be set.')
        sys.exit(1)

    try:
        # perform download
        download_count = do_download(args.bucket,
                                     args.pattern,
                                     os.environ['AWS_ACCESS_KEY_ID'],
                                     os.environ['AWS_SECRET_ACCESS_KEY'],
                                     args.target_dir,
                                     verbose=True)

        print('Downloaded {} object(s) from bucket "{}"'
              .format(download_count, args.bucket))
    except Exception as ex:
        print('Error. {}'.format(ex))
        # exit with non-zero return code
        sys.exit(1)


if __name__ == '__main__':
    main()
