#!/usr/bin/env python
"""Aws s3 interaction helper functions"""
########################################################################
# File: aws.py
#  executable: aws.py
#
# Author: Andrew Bailey
# History: 03/27/19 Created
########################################################################

import boto3
import botocore
import os
import warnings


class AwsS3(object):
    """Class to deal with getting information from aws s3"""

    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, profile_name=None):

        self.session = boto3.Session(profile_name=profile_name,
                                     aws_access_key_id=aws_access_key_id,
                                     aws_secret_access_key=aws_secret_access_key)

        self.s3_resource = self.session.resource('s3')
        self.s3_client = self.session.client('s3')

        self.connected = self.setup()

    def setup(self):
        """Hide unnecessary warnings"""
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")
        try:
            a = [x for x in self.s3_resource.buckets.all()]
            a = [x for x in self.s3_client.list_buckets()]
        except Exception as e:
            return False
        return True

    def download_object(self, path, dest):
        """Download file from specified path
        :param path: path to file
        :param dest: path to directory or renamed file output
        """
        bucket, key = self.split_name(path)
        if os.path.isdir(dest):
            dest = os.path.join(dest, os.path.basename(key))
        assert os.path.exists(os.path.dirname(dest)), \
            "Destination directory does not exist: {}".format(os.path.dirname(dest))
        try:
            self.s3_resource.Bucket(bucket).download_file(key, dest)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist. {}".format(path))
                dest = False
            else:
                raise e
        return dest

    def upload_object(self, file_path, destination, use_original_name=True):
        """Upload a file to s3 bucket
        :param use_original_name: boolean option to use the basename of original file
        :param file_path: path to file to upload
        :param destination: location to place file
        :return: True
        """
        assert os.path.exists(file_path), "File path does not exist {}".format(file_path)
        bucket_name, save_path = self.split_name(destination)
        if use_original_name:
            save_path = os.path.join(save_path, os.path.basename(file_path))

        self.s3_client.upload_file(file_path, bucket_name, save_path)
        return os.path.join(bucket_name, save_path)

    def create_bucket(self, bucket_name, region="us-west-2"):
        """Create a bucket
        :param bucket_name: name of bucket
        :param region: region to place bucket
        """
        self.s3_resource.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={
            'LocationConstraint': region})
        return True

    def delete_bucket(self, bucket_name):
        """Delete a bucket
        :param bucket_name: name of bucket to delete
        :return: True
        """
        bucket = self.s3_resource.Bucket(bucket_name)
        for key in bucket.objects.all():
            key.delete()
        bucket.delete()
        return True

    def bucket_exists(self, bucket_name):
        """Check if bucket exists
        :param bucket_name: name of bucket to create
        :return: True if exists False if not
        """
        self.s3_resource.Bucket(bucket_name)
        exists = True
        try:
            self.s3_resource.meta.client.head_bucket(Bucket=bucket_name)
        except botocore.exceptions.ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            error_code = e.response['Error']['Code']
            if error_code == '404':
                exists = False
        return exists

    def object_exists(self, object_path):
        """Return True if object exists
        :param object_path: path to object
        """
        bucket_name, save_path = self.split_name(object_path)
        try:
            self.s3_resource.Object(bucket_name, save_path).load()
        except botocore.exceptions.ClientError as e:
            return False
        return True

    def delete_object(self, object_path):
        """Delete object in s3
        :param object_path: path to object to delete
        """
        bucket_name, save_path = self.split_name(object_path)
        self.s3_client.delete_object(Bucket=bucket_name, Key=save_path)
        return True

    @staticmethod
    def split_name(name):
        """Split a name to get bucket and key path
        :param name: path to bucket or key
        """
        split_name = [x for x in name.split("/") if x is not '']
        bucket_name = split_name[0]
        key_path = "/".join(split_name[1:])
        return bucket_name, key_path

    def list_objects(self, path):
        """Return a list of full paths to objects within key or bucket
        :param path: path to bucket or key
        """
        return [x for x in self.list_objects_generator(path)]

    def folder_exists(self, path):
        """Check to see if folder exists
        :param path: path to folder
        """
        bucket_name, save_path = self.split_name(path)
        if self.bucket_exists(bucket_name):
            try:
                result = self.s3_client.list_objects(Bucket=bucket_name, Prefix=save_path)
                if result["Contents"]:
                    return True
            except (botocore.exceptions.ClientError, KeyError) as e:
                # The object does not exist.
                return False
        return False

    def list_buckets(self):
        """List all bucket names accessible by s3 client"""
        return [x["Name"] for x in self.s3_client.list_buckets()["Buckets"]]

    def list_objects_generator(self, path, ext=""):
        """
        Generate objects in an S3 bucket.
        source: https://alexwlchan.net/2019/07/listing-s3-keys/
        :param path: path to folder
        :param ext: Only fetch objects whose keys end with
            this suffix (optional).
        """
        assert self.folder_exists(path), "AWS object '{}' does not exist".format(path)
        bucket, prefix = self.split_name(path)
        paginator = self.s3_client.get_paginator("list_objects_v2")

        kwargs = {'Bucket': bucket}

        # We can pass the prefix directly to the S3 API.  If the user has passed
        # a tuple or list of prefixes, we go through them one by one.
        if isinstance(prefix, str):
            prefixes = (prefix, )
        else:
            prefixes = prefix

        for key_prefix in prefixes:
            kwargs["Prefix"] = key_prefix

            for page in paginator.paginate(**kwargs):
                try:
                    contents = page["Contents"]
                except KeyError:
                    return

                for obj in contents:
                    key = obj["Key"]
                    if key.endswith(ext):
                        yield os.path.join(bucket, key)

