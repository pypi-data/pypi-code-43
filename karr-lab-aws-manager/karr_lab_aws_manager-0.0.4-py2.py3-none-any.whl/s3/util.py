from karr_lab_aws_manager.config import config
from pathlib import Path


class S3Util(config.establishS3):

    def __init__(self, profile_name=None, credential_path=None, config_path=None):
        ''' Interacting with aws s3 buckets
        '''
        super().__init__(profile_name=profile_name, credential_path=credential_path, config_path=config_path)


    def download_dir(self, dist, bucket, local='/tmp'):
        ''' Download all contents in a directory in s3 bucket iteratively
            Args:
                dist (:obj: `str`): s3 directory key representation
                bucket (:obj: `str`): name of bucket
                local (:obj: `str`): local directory to store downloaded content
        '''
        paginator = self.client.get_paginator('list_objects')
        for result in paginator.paginate(Bucket=bucket, Delimiter='/', Prefix=dist):
            if result.get('CommonPrefixes') is not None:
                for subdir in result.get('CommonPrefixes'):
                    self.download_dir(subdir.get('Prefix'), bucket, local=local)
            for file in result.get('Contents', []):
                dest_pathname = Path(local, file.get('Key'))
                if file.get('Key').endswith('/'):
                    dest_pathname.mkdir(parents=True, exist_ok=True)
                else:
                    Path(dest_pathname.parent).mkdir(parents=True, exist_ok=True)
                    dest_pathname.touch()
                self.resource.meta.client.download_file(bucket, file.get('Key'), str(dest_pathname))
