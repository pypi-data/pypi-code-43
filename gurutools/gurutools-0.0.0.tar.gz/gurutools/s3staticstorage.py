from django.conf import settings
# from storages.backends.s3boto import S3BotoStorage
from storages.backends.s3boto3 import S3Boto3Storage

class S3StaticStorage(S3Boto3Storage):

    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = settings.AWS_STATIC_STORAGE_BUCKET_NAME
        super(S3StaticStorage, self).__init__(*args, **kwargs)
