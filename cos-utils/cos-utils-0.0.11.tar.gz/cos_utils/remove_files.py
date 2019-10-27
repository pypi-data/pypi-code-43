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
# This utility removes objects in an existing bucket in
# a Cloud Object Storage instance on IBM Cloud.
#


import argparse
import os
import sys

from .cos import COSWrapper, COSWrapperError


class RemoveError(Exception):
    pass


def do_remove(bucket,
              access_key_id,
              secret_access_key,
              object_spec='*',
              verbose=False):
    """
    Clear content of the specified bucket.

    :param bucket: Source bucket name. (Must exist)
    :type bucket: str
    :param access_key_id: HMAC access key id
    :type access_key_id: str
    :param secret_access_key: HMAC secret access key
    :type secret_access_key: str

    :param object_spec: [description], defaults to '*'
    :type object_spec: str, optional
    :param verbose: [description], defaults to False
    :type verbose: bool, optional

    :raises ValueError: A required parameter value is missing.
    :raises RemoveError: Object removal failed due to the specified reason.

    :return: Number of removed objects
    :rtype: int
    """

    if not bucket:
        raise ValueError('Parameter "bucket" is required')

    if not access_key_id:
        raise ValueError('Parameter "access_key_id" is required')

    if not secret_access_key:
        raise ValueError('Parameter "secret_access_key" is required')

    try:
        # instantiate Cloud Object Storage wrapper
        cw = COSWrapper(access_key_id,
                        secret_access_key)
    except COSWrapperError as cwe:
        raise RemoveError('Cannot access Cloud Object Storage: {}'
                          .format(cwe))

    # fetch list of objects in the bucket
    try:
        return cw.clear_bucket(bucket)
    except Exception as ex:
        # catch and mask exception
        raise RemoveError('Cleaning of bucket "{}" failed: {}'
                          .format(bucket, ex))


def main():

    epilog_msg = 'Environment variables AWS_ACCESS_KEY_ID and ' \
                 'AWS_SECRET_ACCESS_KEY must be defined to run the utility.'

    parser = argparse.ArgumentParser(description='Remove objects from a '
                                                 'Cloud Object '
                                                 'Storage bucket.',
                                     epilog=epilog_msg)
    parser.add_argument('bucket',
                        help='Bucket name')

    # parser.add_argument('-p',
    #                     '--pattern',
    #                     help='Object specification '
    #                          '(supported wildcards: * and ?)')

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
        # perform listing
        object_count = do_remove(args.bucket,
                                 os.environ['AWS_ACCESS_KEY_ID'],
                                 os.environ['AWS_SECRET_ACCESS_KEY'],
                                 verbose=True)

        print('Removed {} object(s) from bucket "{}".'
              .format(object_count, args.bucket))
    except Exception as ex:
        print('Error. {}'.format(ex))
        # exit with non-zero return code
        sys.exit(1)


if __name__ == '__main__':
    main()
