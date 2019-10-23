import re
import threading

import boto3
import boto3.s3.transfer
import botocore.config


CHUNKSIZE = 8 << 20  # 8 MB
BOTO_CONFIG = botocore.config.Config(signature_version='s3v4', retries={'max_attempts': 3})
S3_TRANSFER_CONFIG = boto3.s3.transfer.TransferConfig(io_chunksize=CHUNKSIZE)
THREAD_LOCAL = threading.local()


class S3Destination:
    """Generator yielding `store()/delete()`-able S3Files in a bucket/prefix"""
    def __init__(self, bucket, prefix=''):
        self.bucket = bucket
        self.prefix = prefix
        self.delete_lock = threading.Lock()
        self.delete_keys = []

    def __iter__(self):
        s3 = create_s3_client()
        paginator = s3.get_paginator('list_objects')
        for page in paginator.paginate(Bucket=self.bucket, Prefix=self.prefix):
            for content in page.get('Contents', []):
                relpath = re.sub(fr'^{self.prefix}', '', content['Key'])
                yield self.file(relpath, info=content)

    def file(self, relpath, info=None):
        return S3File(self, relpath, info=info)

    def add_delete_key(self, key):
        with self.delete_lock:
            self.delete_keys.append(key)
            if len(self.delete_keys) == 1000:
                self.cleanup()

    def cleanup(self):
        if self.delete_keys:
            s3 = create_s3_client()
            delete = {'Objects': [{'Key': key} for key in self.delete_keys]}
            s3.delete_objects(Bucket=self.bucket, Delete=delete)
            self.delete_keys = []


class S3File:
    """Store read()-ables / delete files on S3"""

    __slots__ = ('name', 'size', 'modified', 's3dst', 'key')

    def __init__(self, s3dst, relpath, info=None):
        self.s3dst = s3dst
        self.name = relpath
        self.key = f'{s3dst.prefix}{relpath}'
        if info is not None:
            self.size = info['Size']
            self.modified = info['LastModified'].timestamp()

    def store(self, src_file):
        """Store `read()`-able on S3"""
        s3 = create_s3_client()
        s3.upload_fileobj(src_file, self.s3dst.bucket, self.key, Config=S3_TRANSFER_CONFIG)

    def delete(self):
        """Delete the S3 object"""
        self.s3dst.add_delete_key(self.key)


def create_s3_client():
    """Create S3 client using default credentials (per thread)"""
    if not hasattr(THREAD_LOCAL, 's3'):
        THREAD_LOCAL.s3 = boto3.client('s3', config=BOTO_CONFIG)
    return THREAD_LOCAL.s3
