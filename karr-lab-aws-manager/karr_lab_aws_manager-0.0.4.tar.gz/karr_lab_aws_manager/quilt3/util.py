import quilt3
from karr_lab_aws_manager.config import config
from karr_lab_aws_manager.s3 import util as s3_util
import json
from configparser import ConfigParser
from pathlib import Path, PurePath
import tempfile
from boto3.s3.transfer import TransferConfig


class QuiltUtil:

    def __init__(self, base_path=None, profile_name=None, default_remote_registry=None,
                aws_path=None, cache_dir=None):
        ''' Handle Quilt authentication file creation without having to use quilt3.login()
            Args:
                aws_path (:obj: `str`): directory in which aws credentials file resides
                base_path (:obj: `str`): directory to store quilt3 credentials generated from aws credentials
                profile_name (:obj: `str`): AWS credentials profile name for quilt
                default_remote_registry (:obj: `str`): default remote registry to store quilt package
                cache_dir (:obj: `str`): default directory to store data
        '''
        self.cache_dir = cache_dir
        self.profile_name = profile_name
        base_path_obj = Path(base_path)
        aws_path_obj = Path(aws_path)
        quilt3.session.AUTH_PATH = base_path_obj / 'auth.json'
        quilt3.session.CREDENTIALS_PATH = base_path_obj / 'credentials.json'
        quilt3.session.AUTH_PATH.touch()
        self.auth_path = quilt3.session.AUTH_PATH
        self.quilt_credentials_path = quilt3.session.CREDENTIALS_PATH

        self.aws_credentials_path = aws_path_obj / 'aws_credentials'
        config = ConfigParser()
        config.read(self.aws_credentials_path.expanduser())
        dic = {'access_key': config[profile_name]['aws_access_key_id'],
               'secret_key': config[profile_name]['aws_secret_access_key'],
               'token': None,
               'expiry_time': config[profile_name]['expiry_time']}
        with open(str(self.quilt_credentials_path), 'w') as f:
            json.dump(dic, f)
        quilt3.config(default_remote_registry=default_remote_registry)
        self.package = quilt3.Package()

    def bucket_obj(self, bucket_uri):
        ''' Create quilt3 bucket object
            Args:
                bucket_uri (:obj: `str`): quilt s3 bucket address
            Return:
                (:obj: `quilt3.Bucket`): quilt3 bucket object
        '''
        return quilt3.Bucket(bucket_uri)

    def add_to_package(self, destination=None, source=None, meta=None):
        ''' Specifically used for uploading datanator package to
            quilt3
            Args:
                source (:obj: `list` of :obj: `str`): sources to be added to package,
                                                      directories must end with '/'
                destination (:obj: `list` of :obj: `str` ): package(s) to be manipulated,
                                                            directories must end with '/'
                meta (:obj: `list` of :obj: `dict`): package meta
            Return:

        '''
        length = len(destination)
        if not (all(len(lst)) == length for lst in [source, meta]):
            return 'All three entries must be lists of the same length.'
        suffix = '/'
        for i, d in enumerate(destination):
            s = source[i]
            m = meta[i]
            if s.endswith(suffix) != d.endswith(suffix): # when s and d do not share the same suffix
                return '{} and {} must have the same suffix. Operation stopped at {}th element.'.format(d, s, i)

            if s.endswith(suffix):
                self.package.set_dir(d, s, meta=m)
            else:
                self.package.set(d, s, meta=m)

    def push_to_remote(self, package, package_name, destination=None, message=None) -> str:
        ''' Push local package to remote registry
            Args:
                package (:obj: `quilt3.Package()`): quilt pacakge
                package_name (:obj: `str`): name of package in "username/packagename" format
                destination (:obj: `str`): file landing destination in remote registry
                message (:obj: `str`): commit message
        '''
        try:
            package.push(package_name, dest=destination, message=message)
        except quilt3.util.QuiltException as e:
            return str(e)

    def build_from_external_bucket(self, package_dest, bucket_name, key, file_dir,
                                  bucket_credential=None, profile_name=None, meta=None,
                                  bucket_config=None, max_concurrency=10):
        ''' Build package with source from external (non-quilt)
            s3 buckets
            Args:
                package_dest (:obj: `str`): package(s) to be manipulated
                bucket_name (:obj: `str`): s3 bucket name
                key (:obj: `str`): the name of the key to download from
                file_dir (:obj: `str`): the path to the file to download to
                bucket_credential (:obj: `str`): directory in which credential for s3 bucket is stored
                profile_name (:obj: `str`): profile to be used for authentication
                meta (:obj: `dict`): meta information for package file
                bucket_credential (:obj: `str`): directory in which config for s3 bucket is stored
                max_concurrency (:obj: `int`): threads used for downloading
        '''
        settings = TransferConfig(max_concurrency=max_concurrency)
        if bucket_credential is None:
            bucket_credential = str(self.aws_credentials_path.expanduser())
        else:
            bucket_credential = str(Path(bucket_credential).expanduser())

        if bucket_config is None:
            bucket_config = str(self.aws_credentials_path.with_name('aws_config').expanduser())
        else:
            bucket_config = str(Path(bucket_config).expanduser())

        if profile_name is None:
            profile_name = self.profile_name

        s3 = s3_util.S3Util(profile_name=profile_name, credential_path=bucket_credential,
                            config_path=bucket_config)
                            
        file_name_path = Path(file_dir, key).expanduser()
        file_name = str(file_name_path)
        if package_dest.endswith('/'):
            file_name_path.mkdir(parents=True, exist_ok=True)
            s3.download_dir(key, bucket_name, local=file_dir)
        else:
            Path(file_name_path.parent).mkdir(parents=True, exist_ok=True)
            file_name_path.touch(exist_ok=True)        
            s3.client.download_file(bucket_name, key, file_name, Config=settings)
        
        if package_dest.endswith('/'):
            return self.package.set_dir(package_dest, file_name, meta=meta)
        else:
            return self.package.set(package_dest, file_name, meta=meta)



# def main():
#     manager = QuiltUtil(aws_path='.wc/third_party',
#                         base_path=tempfile.mkdtemp(), profile_name='quilt-s3',
#                         default_remote_registry='s3://karrlab')
#     p = manager.package
#     p = p.set_dir('/', 's3://karrlab/datanator/')
#     p.set_meta({"package-type": 'mongodb data dump'})
#     p.push('karrlab/datanator')

# if __name__ == '__main__':
#     main()