from pathlib import Path
import boto3
import os
from configparser import ConfigParser
from requests_aws4auth import AWS4Auth


class credentialsFile:
    
    def __init__(self, credential_path=None, config_path=None, profile_name=None):
        ''' Establish environment variables' paths
        '''
        if profile_name is None:
            profile_name = 'test'
        if os.getenv('AWS_ACCESS_KEY_ID') is None:
            self.AWS_SHARED_CREDENTIALS_FILE = str(Path(credential_path).expanduser())
            self.AWS_CONFIG_FILE = str(Path(config_path).expanduser())
            os.environ['AWS_SHARED_CREDENTIALS_FILE'] = self.AWS_SHARED_CREDENTIALS_FILE
            os.environ['AWS_CONFIG_FILE'] = self.AWS_CONFIG_FILE
            credentials = ConfigParser()
            credentials.read(self.AWS_SHARED_CREDENTIALS_FILE)
            config = ConfigParser()
            config.read(self.AWS_CONFIG_FILE)
            os.environ['AWS_PROFILE'] = profile_name
            os.environ['AWS_ACCESS_KEY_ID'] = credentials[profile_name]['aws_access_key_id']
            os.environ['AWS_SECRET_ACCESS_KEY'] = credentials[profile_name]['aws_secret_access_key']
            os.environ['AWS_DEFAULT_REGION'] = config['profile ' + profile_name]['region']
        else:
            os.environ['AWS_PROFILE'] = profile_name
            os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
            os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
            os.environ['AWS_DEFAULT_REGION'] = os.getenv('AWS_DEFAULT_REGION')         


class establishSession(credentialsFile):
    
    def __init__(self, credential_path=None, config_path=None, profile_name=None,
                service_name=None):
        super().__init__(credential_path=credential_path, config_path=config_path,
                        profile_name=profile_name)
        self.session = boto3.Session(profile_name=profile_name)
        self.access_key = self.session.get_credentials().access_key
        self.secret_key = self.session.get_credentials().secret_key
        self.region = self.session.region_name
        self.awsauth = AWS4Auth(self.access_key, self.secret_key,
                           self.region, service_name)


class establishES(establishSession):

    def __init__(self, credential_path=None, config_path=None, profile_name=None,
                elastic_path=None, service_name='es'):
        super().__init__(credential_path=credential_path, config_path=config_path,
                        profile_name=profile_name, service_name=service_name)
        self.client = self.session.client(service_name)
        self.es_config = str(Path(elastic_path).expanduser())
        config = ConfigParser()
        config.read(self.es_config)
        self.es_endpoint = config['elasticsearch-endpoint']['address']


class establishS3(establishSession):

    def __init__(self, credential_path=None, config_path=None, profile_name=None, service_name='s3'):
        super().__init__(credential_path=credential_path, config_path=config_path, profile_name=profile_name,
                        service_name=service_name)
        self.resource = self.session.resource(service_name)
        self.client = self.resource.meta.client