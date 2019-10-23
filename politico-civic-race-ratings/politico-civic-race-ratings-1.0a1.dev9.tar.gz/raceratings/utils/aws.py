# Imports from Django.
from django.conf import settings


# Imports from other dependencies.
import boto3
from storages.backends.s3boto3 import S3Boto3Storage


AWS_CONFIG = dict(
    region=getattr(settings, "RACE_RATINGS_AWS_REGION", None),
    access_key=getattr(settings, "RACE_RATINGS_AWS_ACCESS_KEY_ID", None),
    secret_key=getattr(settings, "RACE_RATINGS_AWS_SECRET_ACCESS_KEY", None),
    s3_bucket=getattr(settings, "RACE_RATINGS_AWS_S3_BUCKET", None),
    s3_upload_root=getattr(
        settings, "RACE_RATINGS_S3_UPLOAD_ROOT", "uploads/raceratings"
    ),
    custom_cloudfront_domain=getattr(
        settings, "RACE_RATINGS_CLOUDFRONT_ALTERNATE_DOMAIN", None
    ),
)


def get_bucket():
    session = boto3.session.Session(
        region_name=AWS_CONFIG.get("region"),
        aws_access_key_id=AWS_CONFIG.get("access_key"),
        aws_secret_access_key=AWS_CONFIG.get("secret_key"),
    )
    s3 = session.resource("s3")

    return s3.Bucket(AWS_CONFIG.get("s3_bucket"))


class Defaults(object):
    CACHE_HEADER = str("max-age=5")

    ROOT_PATH = "elections"

    if AWS_CONFIG.get("s3_bucket") == "interactives.politico.com":
        ACL = "public-read"
    else:
        ACL = "private"


defaults = Defaults


class StorageService(S3Boto3Storage):
    bucket_name = AWS_CONFIG.get("s3_bucket")
    access_key = AWS_CONFIG.get("access_key")
    secret_key = AWS_CONFIG.get("secret_key")
    file_overwrite = True
    querystring_auth = False
    object_parameters = {"CacheControl": "max-age=86400", "ACL": "public-read"}
    custom_domain = AWS_CONFIG.get("custom_cloudfront_domain")
    location = AWS_CONFIG.get("s3_upload_root")
