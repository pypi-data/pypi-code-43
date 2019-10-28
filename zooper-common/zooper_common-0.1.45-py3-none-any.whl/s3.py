"""S3 Utility.

S3 zooper toolbox.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import object
import errno
import os

import boto3


class S3Utility(object):
    """ S3Utility class.

    Usage:
    s3 = S3Utility()
    s3.upload_folder(file_name, bucket='bucket_name', prefix='images')
    s3.download_file(bucket_name, key, target)
    """
    ACCESS_KEY = 'AKIA3ZXWQQGBJ5NZ4YUO'
    SECRET_KEY = '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'
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.ACCESS_KEY,
            aws_secret_access_key=self.SECRET_KEY)
        session = boto3.Session(
            aws_access_key_id=self.ACCESS_KEY,
            aws_secret_access_key=self.SECRET_KEY
        )
        self.s3_session_resource = session.resource('s3')
        self.s3_resource = boto3.resource(
            's3',
            aws_access_key_id=self.ACCESS_KEY,
            aws_secret_access_key=self.SECRET_KEY
        )

    def upload_folder(self, path, bucket=None, prefix=None):
        """ Upload a folder or file to target bucket/prefix """
        files = []
        key_suffix = None
        if os.path.isdir(path):
            for (dirpath, dirnames, filenames) in os.walk(path):
                for name in filenames:
                    local_path = os.path.join(dirpath, name)
                    s3_relative_prefix = '' if path == dirpath else os.path.relpath(dirpath, start=path) + '/'
                    s3_key = '{}/{}{}'.format(prefix, s3_relative_prefix, name)
                    files.append((local_path, s3_key))
        else:
            _, name = os.path.split(path)
            if prefix is None or prefix is '':
              s3_key = '{}'.format(name)
            else:
              s3_key = '{}/{}'.format(prefix, name)
            files.append((path, s3_key))
            key_suffix = name

        for local_path, s3_key in files:
            self.s3_session_resource.Object(bucket, s3_key).upload_file(local_path)

        s3_uri = ('s3://{}'.format(bucket) if prefix is None or prefix is ''
                  else 's3://{}/{}'.format(bucket, prefix))
        # If a specific file was used as input (instead of a directory), we return the full S3 key
        # of the uploaded object. This prevents unintentionally using other files under the same prefix
        # during training.
        if key_suffix:
            s3_uri = '{}/{}'.format(s3_uri, key_suffix)
        return s3_uri

    def download_file(self, bucket_name, key, target):
        """ Download a file.

        Usage:
        s3.download_file('mybucket', 'images', '/tmp/file.jpg')
        """
        print('Downloading {}/{} to {} ...'.format(bucket_name, key, target))
        self.s3_resource.Bucket(bucket_name).download_file(key, target)

    def download_folder(self, bucket_name, prefix, target):
        """ Download folder (bucket_name/prefix) to a target on local storage """
        bucket = self.s3_session_resource.Bucket(bucket_name)

        prefix = prefix.lstrip('/')

        print('Downloading bucket {}/{} to {} ...'.format(bucket_name, prefix, target))
        # there is a chance that the prefix points to a file and not a 'directory' if that is the case
        # we should just download it.
        objects = list(bucket.objects.filter(Prefix=prefix))

        if len(objects) > 0 and objects[0].key == prefix and prefix[-1] != '/':
            self.s3_session_resource.Object(bucket_name, prefix).download_file(os.path.join(target, os.path.basename(prefix)))
            return

        # the prefix points to an s3 'directory' download the whole thing
        for obj_sum in bucket.objects.filter(Prefix=prefix):
            # if obj_sum is a folder object skip it.
            if obj_sum.key != '' and obj_sum.key[-1] == '/':
                continue
            obj = self.s3_session_resource.Object(obj_sum.bucket_name, obj_sum.key)
            s3_relative_path = obj_sum.key[len(prefix):].lstrip('/')
            file_path = os.path.join(target, s3_relative_path)

            try:
                os.makedirs(os.path.dirname(file_path))
            except OSError as exc:
                # EXIST means the folder already exists, this is safe to skip
                # anything else will be raised.
                if exc.errno != errno.EEXIST:
                    raise
                pass
            if not os.path.exists(file_path):
                print('Downloading {} ...'.format(file_path))
                obj.download_file(file_path)
            else:
                print('Skip file {}, already exists'.format(file_path))

    def get_presigned_url(self, bucket, key, expires_seconds=3600):
        # Generate the URL to get 'key-name' from 'bucket-name'
        url = self.s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket,
                'Key': key
            },
            ExpiresIn=expires_seconds
        )
        return url

    def sync(self, source, dest):
        command = "aws s3 sync {} {}".format(source, dest)
        os.system(command)

    def key_exist(self, bucket_name, key):
        bucket = self.s3_resource.Bucket(bucket_name)
        try:
            iter(bucket.objects.filter(Prefix=key)).next()
            return True
        except StopIteration:
            return False
