# Imports from other dependencies.
import boto3


# Imports from civic_utils.
from civic_utils.conf import settings


def get_s3_session():
    return boto3.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def get_bucket(bucket_name):
    session = get_s3_session()
    s3 = session.resource("s3")
    return s3.Bucket(bucket_name)
