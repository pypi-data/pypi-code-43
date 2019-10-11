from urllib import parse
from botocore.exceptions import ClientError
import logging

# Parse the bucketname -and do a boto call to see if the bucket exists
# verify that bucket is in the same region as VPC


def s3_buckets_are_valid(logbucket, databucket, vpc_region, s3client, issues):

    for bucket in [logbucket, databucket]:
        s3_bucket_is_valid(bucket, vpc_region, s3client, issues)
    return


def s3_bucket_is_valid(bucket, vpc_region, s3client, issues):
    parseresult = parse.urlsplit(bucket)
    if not parseresult[0] == 's3a':
        issues.append(
            "S3: Provided bucket name ({}) is not of the format s3a://<bucketname>/<path>".format(bucket))
        return

    bucketname = parseresult[1]

    # Need try/except here because s3 client raises an exception if the bucketname does not exist
    # The other option was to use s3 resource, but there isn't any way of getting bucket location
    # from the resource object
    try:
        response = s3client.get_bucket_location(
            Bucket=bucketname)
        bucket_region = response["LocationConstraint"]
        if bucket_region == None:
            bucket_region = 'us-east-1'
        if bucket_region != vpc_region:
            msg = "s3a: Unexpected: Bucket {} in {} region. VPC in {} region. They should be the same region".format(
                bucketname, bucket_region, vpc_region)
            issues.append(msg)
    except ClientError as e:
        logging.getLogger(__name__).warning(
            "Skipping bucket check because this error occurred: {}".format(e))
