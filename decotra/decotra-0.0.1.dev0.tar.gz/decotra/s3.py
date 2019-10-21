import os
import pickle

import boto3
from botocore.client import Config
import numpy as np

import decotra


def upload_to_s3(
        bucket_prefix,
        saved_prefix,
        upload_to_prefix,
        filename):
    s3 = boto3.resource(
        's3',
        endpoint_url=os.getenv('S3_ENDPOINT_URL') if os.getenv('S3_ENDPOINT_URL') != '' else None,
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )
    s3.Bucket(bucket_prefix).upload_file(f'{saved_prefix}{filename}', f'{upload_to_prefix}{filename}')
    return


def track(bucket_name):
    def _save_and_upload(func):
        def runner(*args, **kwargs):
            result = func(*args, **kwargs)
            os.makedirs(decotra.saved_prefix, exist_ok=True)

            # saving
            if type(result) is np.ndarray:
                np.savez(decotra.saved_prefix + func.__name__, result)
            else:
                with open(decotra.saved_prefix + func.__name__ + '.pkl', 'wb') as f:
                    pickle.dump(result, f)

            filename = func.__name__ + '.npz' if type(result) else func.__name__ + '.pkl'

            # uploading
            upload_to_s3(
                bucket_prefix=bucket_name,
                saved_prefix=decotra.saved_prefix,
                upload_to_prefix=decotra.saved_prefix,
                filename=filename
            )

            return result
        return runner
    return _save_and_upload

