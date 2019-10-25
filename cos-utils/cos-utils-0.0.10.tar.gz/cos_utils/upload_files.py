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
# This utility uploads one or more files to an existing bucket in
# a Cloud Object Storage instance on IBM Cloud.
#


import argparse
import glob
import os
import sys

from pathlib import Path

from .cos import COSWrapper, COSWrapperError


class UploadError(Exception):
    pass


def do_upload(bucket,
              source_spec,
              access_key_id,
              secret_access_key,
              prefix=None,
              wipe=False,
              squash=False,
              recursive=False,
              verbose=False):
    """
    Uploads the file(s) identified by source_spec to
    the specified Cloud Object Storage bucket.

    :param bucket: Target bucket name.
    :type bucket: str
    :param source_spec: Identifies a file, multiple files
    or a directory in the local file system.
    :type source_spec: str
    :param access_key_id: HMAC access key id
    :type access_key_id: str
    :param secret_access_key: HMAC secret access key
    :type secret_access_key: str
    :param prefix: prefix to be added to file name when
    the object key is generated, defaults to None
    :type prefix: str, optional
    :param wipe: remove objects from bucket before upload,
    defaults to False
    :type wipe: bool, optional
    :param squash: exclude path information from object key,
    defaults to False
    :type squash: bool, optional
    :param recursive: include files in subdirectories,
    defaults to False
    :type recursive: bool, optional
    :param verbose: print diagnostic information, defaults to False
    :type verbose: bool, optional
    :raises ValueError: A required parameter value is missing.
    :raises UploadError: Upload failed due to the specified reason.
    :return: Number of uploaded objects
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

    try:
        # instantiate Cloud Object Storage wrapper
        cw = COSWrapper(access_key_id,
                        secret_access_key)
    except COSWrapperError as cwe:
        raise UploadError('Cannot access Cloud Object Storage: {}'
                          .format(cwe))

    # remove all objects from the specified bucket
    try:
        if wipe:
            if verbose:
                print('Clearing bucket "{}" ...'.format(bucket))
            cw.clear_bucket(bucket)
    except Exception as ex:
        raise UploadError('Clearing of bucket "{}" failed: {}'
                          .format(bucket, ex))

    # upload files matching the source specification
    try:
        file_count = 0

        if os.path.isdir(source_spec):
            # source specification identifies a directory
            base_dir = source_spec.rstrip(os.path.sep)

            if recursive:
                pattern = '**/*'
            else:
                pattern = '*'

            for file in Path(base_dir).glob(pattern):
                file = str(file)

                if not os.path.isfile(file):
                    # can only upload files
                    continue

                if squash:
                    # remove directory offset information
                    key = os.path.basename(file[len(base_dir):])
                else:
                    key = file[len(base_dir)+1:]

                if prefix:
                    # add key name prefix
                    key = '{}/{}'.format(prefix.rstrip('/'), key)

                if verbose:
                    print('Uploading "{}" => "{}"'.format(file, key))

                # upload object to Cloud Object Storage
                cw.upload_object(file,
                                 bucket,
                                 key)

                file_count = file_count + 1

            if file_count == 0:
                raise UploadError('No files match the source specification {}'
                                  .format(source_spec))
            return

        # source specification likely identifies one or more files
        base_dir = os.path.dirname(source_spec)
        if recursive:
            pattern = '{}/**/{}'.format(base_dir,
                                        os.path.basename(source_spec))
        else:
            pattern = source_spec

        for file in glob.iglob(pattern,
                               recursive=True):
            if not os.path.isfile(file):
                # can only upload files
                continue

            if squash:
                # remove directory offset information
                key = os.path.basename(file[len(base_dir):])
            else:
                key = file[len(base_dir)+1:]

            if prefix:
                # add key name prefix
                key = '{}/{}'.format(prefix.rstrip('/'), key)

            if verbose:
                print('Uploading "{}" => "{}"'.format(file, key))

            # upload object to Cloud Object Storage
            cw.upload_object(file,
                             bucket,
                             key)

            file_count = file_count + 1

        if file_count == 0:
            raise UploadError('No files match the source specification {}'
                              .format(source_spec))

        # return number of uploaded files
        return file_count

    except UploadError:
        # bubble up
        raise
    except Exception as ex:
        # catch and mask exception
        raise UploadError('Upload to bucket "{}" failed: {}'
                          .format(bucket, ex))


def main():

    epilog_msg = 'Environment variables AWS_ACCESS_KEY_ID and ' \
                 'AWS_SECRET_ACCESS_KEY must be defined to run the utility.'

    parser = argparse.ArgumentParser(description='Upload files to a '
                                                 'Cloud Object '
                                                 'Storage bucket.',
                                     epilog=epilog_msg)
    parser.add_argument('bucket',
                        help='Bucket name')
    parser.add_argument('source',
                        help='File or directory spec '
                             '(supported wildcards: * and ?)')
    parser.add_argument('-p',
                        '--prefix',
                        help='Key name prefix')
    parser.add_argument('-r',
                        '--recursive',
                        help='Include files in subdirectories',
                        action='store_true')
    parser.add_argument('-s',
                        '--squash',
                        help='Exclude subdirectory name from key name',
                        action='store_true')
    parser.add_argument('-w',
                        '--wipe',
                        help='Clear bucket prior to upload',
                        action='store_true')

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
        # perform upload
        upload_count = do_upload(args.bucket,
                                 args.source,
                                 os.environ['AWS_ACCESS_KEY_ID'],
                                 os.environ['AWS_SECRET_ACCESS_KEY'],
                                 args.prefix,
                                 args.wipe,
                                 args.squash,
                                 args.recursive,
                                 verbose=True)

        print('Uploaded {} file(s) to bucket "{}"'
              .format(upload_count, args.bucket))
    except Exception as ex:
        print('Error. {}'.format(ex))
        # exit with non-zero return code
        sys.exit(1)


if __name__ == '__main__':
    main()
