"""
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
"""
import logging
from typing import Optional

import boto3
from botocore.exceptions import ClientError

BUCKET_ARN = "arn:aws:s3:::dummy-simple-s3-1570741933910"
BUCKET_NAME = "dummy-simple-s3-1570741933910"


def create_presigned_url(
    bucket_name: str, object_name: str, expiration=3600
) -> Optional[str]:
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client("s3")
    try:
        response = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


if __name__ == "__main__":
    x = create_presigned_url(BUCKET_NAME, "toto.txt")
    print(x)
