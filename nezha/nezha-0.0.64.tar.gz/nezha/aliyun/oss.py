import os

from oss2 import Auth
from oss2 import Bucket


class OSS(object):
    """
    aliyun oss sdk
    """

    def __init__(self, access_key_id: str, access_key_secret: str, bucket_name: str, endpoint: str):
        """

        :param access_key_id: aliyun access_key_id
        :param access_key_secret: aliyun access_key_secret
        :param bucket_name: Bucket名
        :param endpoint: 访问域名或者CNAME
        """
        self.auth = Auth(access_key_id, access_key_secret)
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        self._bucket = None

    @property
    def bucket(self) -> Bucket:
        if not self._bucket:
            endpoint = self.endpoint if self.endpoint.startswith('http') else f'http://{self.endpoint}'
            self._bucket = Bucket(self.auth, endpoint, self.bucket_name)
        return self._bucket

    def sign_url(self, file_path: str, expires=0) -> str:
        """
        generate open http url for file in bucket
        :param file_path: 文件的oss存储路径
        :param expires: 链接有效时间, 如果为 0 则永久有效。
        """
        url = self.bucket.sign_url('GET', file_path, expires)
        if expires:
            return url
        else:
            return url.split('?')[0]

    @staticmethod
    def generate_file_path(dirpath: str, filename: str) -> str:
        """
        generate upload file_path by filename
        :param filename:
        :return:
        """
        return os.path.join(dirpath, filename)

    def upload(self, file_path: str, file: str) -> bool:
        """
        上传文件到oss
        if picture, file type should be binary.
        :param file_path: 文件的oss存储路径
        :param file: 上传文件
        :return: 上传状态
        """
        result = self.bucket.put_object(key=file_path, data=file)
        return result.status == 200
