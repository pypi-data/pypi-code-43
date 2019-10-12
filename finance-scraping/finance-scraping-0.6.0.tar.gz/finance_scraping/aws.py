# this module stores utility functions to interact with AWS

import boto3


def get_s3_key(prefix, suffix, date):
    """
    Get an AWS S3 key formatted with the date.

    :param str prefix: prefix of the S3 key
    :param str suffix: suffix of the S3 key
    :param str date: date
    :return str: AWS S3 key
    """
    key = f"{prefix}/{date}/{suffix}"
    return key


def get_client(service, profile):
    """
    Get an AWS client.

    :param str service: AWS service, e.g. 's3'
    :param str profile: AWS profile
    :return boto3.Client: client for API calls
    """
    client = boto3.Session(profile_name=profile).client(service)
    return client


def download_s3_object(bucket, key, profile):
    """
    Download data from an AWS S3 object.

    :param str bucket: AWS S3 bucket where the object is stored
    :param str key: AWS S3 key to the object
    :para str profile: AWS profile to use
    :return bytes: data from the AWS S3 object
    """
    client = get_client('s3', profile)
    response = client.get_object(Bucket=bucket, Key=key)
    data = response.get('Body').read()
    return data


def upload_object_to_s3(file_object, bucket, key, profile):
    """
    Upload a file-like object to S3.

    :param data: file-like object
    :param str bucket: S3 bucket where to upload data
    :param str key: S3 object key where to upload data
    :para str profile: AWS profile to use
    """
    client = get_client('s3', profile)
    client.put_object(Body=file_object.getvalue(), Bucket=bucket, Key=key)
