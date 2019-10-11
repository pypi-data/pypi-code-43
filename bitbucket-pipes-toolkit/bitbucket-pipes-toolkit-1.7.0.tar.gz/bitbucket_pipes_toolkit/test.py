import os
from unittest import TestCase

from git import Repo

import docker
from docker.errors import ContainerError


class PipeTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.image_tag = 'bitbucketpipelines/demo-pipe-python:ci' + \
            os.getenv('BITBUCKET_BUILD_NUMBER', 'local')
        cls.docker_client = docker.from_env()
        cls.docker_client.images.build(
            path='.', tag=cls.image_tag)

    def _get_pipelines_variables(self):
        variables_names = [
            'BITBUCKET_BUILD_NUMBER',
            'BITBUCKET_PARALLEL_STEP',
            'BITBUCKET_PARALLEL_STEP_COUNT',
            'BITBUCKET_PROJECT_UUID',
            'BITBUCKET_PROJECT_KEY'
        ]

        variables = {name: os.getenv(name, 'local') for name in variables_names}

        current_repo = Repo()

        variables['BITBUCKET_BRANCH'] = os.getenv('BITBUCKET_BRANCH', current_repo.active_branch.name)
        variables['BITBUCKET_COMMIT'] = os.getenv('BITBUCKET_COMMIT', current_repo.commit().hexsha)
        variables['BITBUCKET_REPO_SLUG'] = os.getenv('BITBUCKET_REPO_SLUG', 
                                                     os.path.basename(current_repo.working_tree_dir))
        variables['BITBUCKET_WORKSPACE'] = os.getenv('BITBUCKET_WORKSPACE', 'atlassian')
        variables['BITBUCKET_REPO_OWNER'] = os.getenv('BITBUCKET_REPO_OWNER', 'atlassian')

        return variables

    def run_and_get_container(self, cmd=None, **kwargs):
        pipelines_variables = self._get_pipelines_variables()
        pipelines_variables.update(kwargs.get('environment', {}))
        kwargs['environment'] = pipelines_variables
        # https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run
        cwd = os.getcwd()

        volumes = {cwd: {'bind': cwd, 'mode': 'rw'}}
        if kwargs.get('volumes'):
            volumes.update(kwargs.pop('volumes'))

        try:
            return self.docker_client.containers.run(
                self.image_tag,
                command=cmd,
                volumes=volumes,
                working_dir=cwd,
                detach=True,
                **kwargs
            )
        except ContainerError as e:
            return e.container

    def run_container(self, cmd=None, **kwargs):
        container = self.run_and_get_container(cmd, **kwargs)
        container.wait()

        return container.logs().decode()


