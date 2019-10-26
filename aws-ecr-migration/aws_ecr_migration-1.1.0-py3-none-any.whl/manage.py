import logging
import subprocess
import boto3
import base64

from typing import Any, List
from botocore.exceptions import ClientError
from aws_ecr_migration import root
from aws_ecr_migration.aws_credentials import AwsCredentials

logr = logging.getLogger(__name__)


class Manager:
    def __init__(
            self,
            credentials: AwsCredentials,
            remote_repository: str,
    ) -> None:
        """
        Constructor.

        :param credentials: Aws account credentials that have access to specified ECR repository.
        :param remote_repository: A remote ECR repository URI.
        """
        self.remote_repository = remote_repository

        self.ecr_client = boto3.client(
            'ecr',
            region_name=credentials.region,
            aws_access_key_id=credentials.access_key,
            aws_secret_access_key=credentials.secret_key
        )

    def push_container(self, container: str):
        """
        Commits a current container and pushed a produced docker image to a remote ECR repository.

        :param container: A container id or name to push.

        :return: No return.
        """
        self.__login_and_execute([f'{root}/ecr_push_container.sh', container, self.remote_repository])

    def push_image(self, image: str):
        """
        Pushes given image to a remote ECR repository.

        :param image: Image name or id to push.

        :return: No return.
        """
        self.__login_and_execute([f'{root}/ecr_push_image.sh', image, self.remote_repository])

    def pull(self):
        """
        Pulls docker image from a remote ECR repository.

        :return: No return.
        """
        self.__login_and_execute([f'{root}/ecr_pull.sh', self.remote_repository])

    def repository_exists(self):
        """
        Checks whether a remote repository exists.

        :return: True if exists, false otherwise.
        """
        try:
            self.ecr_client.describe_repositories(
                repositoryNames=[self.remote_repository.split('/')[1]],
            )
            return True
        except ClientError as ex:
            if ex.response['Error']['Code'] == 'RepositoryNotFoundException':
                return False

            raise

    def repository_empty(self):
        """
        Checks whether a remote repository is empty or not.

        :return: True if empty, false otherwise.
        """
        response = self.ecr_client.list_images(
            repositoryName=self.remote_repository.split('/')[1],
        )

        ids = response['imageIds']
        return len(ids) == 0

    def __ecr_login(self) -> str:
        response = self.ecr_client.get_authorization_token()
        auth_token = response['authorizationData'][0]['authorizationToken']
        auth_token = base64.b64decode(auth_token).decode()[4:]
        endpoint = response['authorizationData'][0]['proxyEndpoint']

        return f'docker login -u AWS -p {auth_token} {endpoint}'

    def __login_and_execute(self, command: List[Any]):
        cmd1 = self.__ecr_login()
        cmd2 = ' '.join(command)

        process = subprocess.Popen("bash", shell=True, stdin=subprocess.PIPE, stdout=None, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(f'{cmd1}; {cmd2}'.encode())

        if stdout:
            logr.info(stdout)

        if stderr:
            logr.error(stderr)

        assert process.returncode == 0

        logr.info('Success!')
