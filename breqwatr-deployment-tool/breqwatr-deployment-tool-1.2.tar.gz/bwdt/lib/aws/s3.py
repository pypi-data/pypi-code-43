""" Module for interacting with AWS S3 """
# pylint: disable=import-error
import boto3

import bwdt.lib.auth


class S3(object):
    """ Object class for S3 """
    def __init__(self):
        auth = bwdt.lib.auth.get()
        session = boto3.Session(aws_access_key_id=auth['key_id'],
                                aws_secret_access_key=auth['key'])
        self.client = session.client('s3')

    def download(self, path, bucket_name, key):
        """ Download key from bucket_name to path """
        return self.client.download_file(bucket_name, key, path)

    def upload(self, path, bucket_name, key):
        """ Upload from path to bucket_name as key """
        return self.client.upload_file(path, bucket_name, key)
