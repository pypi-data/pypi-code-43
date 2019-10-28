from cnvrg.modules.storage.storage import Storage
from cnvrg.modules.cnvrg_files import  CnvrgFiles
from typing import Dict
import boto3
from botocore.exceptions import ClientError
import click
import os

class S3Storage(Storage):
    def __init__(self, element: CnvrgFiles, working_dir: str, storage_resp: Dict):
        super().__init__(element, working_dir, storage_resp.get("path_sts"))
        del storage_resp["path_sts"]
        props = self.decrypt_dict(storage_resp, keys=["sts_a", "sts_s", "sts_st", "bucket", "region"])
        self.s3props = {"aws_access_key_id": props.get("sts_a"),
                        "aws_secret_access_key": props.get("sts_s"),
                        "aws_session_token": props.get("sts_st"),
                        "region_name": props.get("region")}
        self.bucket = props.get("bucket")
        self.region = props.get("region")

    def __get_boto_client(self):
        return boto3.client("s3", **self.s3props)

    def download_file(self, local_path: str, storage_path: str):
        try:
            self.__get_boto_client().download_file(self.bucket, storage_path, local_path)
        except ClientError as e:
            click.secho("Got error while downloading {filename}".format(filename=local_path))
            raise e

    def upload_file(self, local_path: str, storage_path: str):
        try:
            with open(os.path.join(self.working_dir, local_path), 'rb') as data:
                self.__get_boto_client().upload_fileobj(data, self.bucket, storage_path)
        except ClientError as e:
            #click.secho("Got error while downloading {filename}".format(filename=local_path))
            raise e