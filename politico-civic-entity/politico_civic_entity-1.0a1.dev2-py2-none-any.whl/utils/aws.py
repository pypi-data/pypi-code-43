# Imports from other dependencies.
from storages.backends.s3boto3 import S3Boto3Storage


# Imports from entity.
from entity.conf import settings


class StorageService(S3Boto3Storage):
    access_key = settings.AWS_ACCESS_KEY_ID
    secret_key = settings.AWS_SECRET_ACCESS_KEY
    bucket_name = settings.AWS_S3_BUCKET
    custom_domain = settings.CLOUDFRONT_ALTERNATE_DOMAIN
    location = settings.S3_UPLOAD_ROOT
    file_overwrite = True
    querystring_auth = False
    object_parameters = {
        "CacheControl": "max-age=86400",
        "ACL": settings.AWS_S3_ACL,
    }
