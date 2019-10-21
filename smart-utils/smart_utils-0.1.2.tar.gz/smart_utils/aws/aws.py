import boto3
from botocore.exceptions import ClientError
import logging


class AWSClient:

    def __init__(self, access_key, secret_key, service):
 
        self.access_key = access_key
        self.secret_key = secret_key
        self.service = service
        self.client = self.__get_client()

    def __get_client(self):

        try:
            client = boto3.client(
                self.service,
                aws_access_key_id= self.access_key,
                aws_secret_access_key= self.secret_key,
            )
            return client
        except Exception as e:
            logging.error("Connection Error {}".format(e))
    
    def get_parameter(self,name):

        try:
            parameter = self.client.get_parameter(
                Name=name,
                WithDecryption=True
            )
            return parameter["Parameter"]["Value"]

        except  ClientError as e:
            logging.warning("{} Not Found".format(name))
