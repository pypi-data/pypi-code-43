""" Container class for interacting with Docker """
import os
import sys
from requests.exceptions import ReadTimeout

# pylint: disable=import-error
import docker
from click import echo

import bwdt.lib.auth
from bwdt.constants import KOLLA_IMAGE_TAGS, SERVICE_IMAGE_TAGS
from bwdt.lib.aws.ecr import ECR


def _all_images():
    """ Return dict of all images """
    images = {}
    images.update(SERVICE_IMAGE_TAGS)
    images.update(KOLLA_IMAGE_TAGS)
    return images


def get_image_as_filename(image_name, tag, directory):
    """ Returns an image as a filename - used for export operations """
    filename_base = image_name.replace('/', '-')
    directory = directory.rstrip('/')
    path = '{}/{}-{}.docker'.format(directory, filename_base, tag)
    return path


def offline_image_exists(image_name, tag):
    """ Return true if the offline image file exists """
    auth = bwdt.lib.auth.get()
    directory = '{}/{}'.format(auth['offline_path'], '/images/')
    path = get_image_as_filename(image_name, tag, directory)
    return os.path.exists(path)


def delete_docker_credential():
    """ Deletes the current docker login file """
    home = os.path.expanduser("~")
    docker_cred_path = '{}/.docker/config.json'.format(home)
    if os.path.exists(docker_cred_path):
        os.remove(docker_cred_path)


class Docker(object):
    """Object to interact with docker & ECR"""
    def __init__(self):
        client = docker.from_env()
        repo_prefix = ""
        if bwdt.lib.auth.use_ecr():
            ecr = ECR()
            delete_docker_credential()
            client.login(
                username=ecr.credentials['username'],
                password=ecr.credentials['password'],
                registry=ecr.credentials['registry'])
            repo_prefix = '{}/'.format(ecr.registry_prefix())
        self.client = client
        self.repo_prefix = repo_prefix

    def _pull_ecr(self, repository, tag, retag=True, remove_long_tag=True):
        """ Pull from ECR's registry """
        echo('Pulling {}:{} from upstream registry'.format(repository, tag))
        full_repo_name = "{}{}".format(self.repo_prefix, repository)
        self.client.images.pull(repository=full_repo_name, tag=tag)
        if retag:
            self.tag(old_repo=full_repo_name, old_tag=tag, new_repo=repository,
                     new_tag=tag)
            if remove_long_tag:
                self.remove(repo=full_repo_name, tag=tag)

    def pull(self, repository, tag=None, retag=True, remove_long_tag=True):
        """ Pull or import an image """
        if tag is None:
            tag = _all_images()[repository]
        if bwdt.lib.auth.use_ecr():
            self._pull_ecr(repository, tag, retag, remove_long_tag)
        else:
            self.import_image(repository, tag)

    def pull_all(self, tag=None, retag=True, remove_long_tag=True):
        """ Pull or import all images """
        all_images = _all_images()
        i = 1
        count = len(all_images)
        for repository in all_images:
            echo('Pulling image {} of {}'.format(i, count))
            i += 1
            self.pull(repository=repository, tag=tag, retag=retag,
                      remove_long_tag=remove_long_tag)

    def tag(self, old_repo, old_tag, new_repo, new_tag):
        """ docker tag """
        old_repo_full = '{}:{}'.format(old_repo, old_tag)
        image = self.client.images.get(old_repo_full)
        image.tag(new_repo, tag=new_tag)

    def remove(self, repo, tag):
        """ Docker rmi """
        image = '{}:{}'.format(repo, tag)
        self.client.images.remove(image=image)

    def retag(self, image_name, tag, new_registry_url):
        """ retag an upstream image to the new_registry_url """
        repository = '{}:{}'.format(image_name, tag)
        image = self.client.images.get(repository)
        new_repository = '{}/{}'.format(new_registry_url, image_name)
        image.tag(new_repository, tag=tag)

    def push(self, image_name, tag, registry_url):
        """ Push an image to a remote registry. Return true if success """
        repository = '{}/{}'.format(registry_url, image_name)
        result = self.client.images.push(repository, tag=tag)
        if 'gave HTTP response to HTTPS' in result:
            echo('ERROR: This registry is not HTTPS and not trusted')
            return False
        return True

    def list(self, **kwargs):
        """ List the running containers """
        if 'all' not in kwargs:
            kwargs['all'] = True
        return self.client.containers.list(**kwargs)

    def get_container(self, name):
        """ Return a container with matching name or None """
        containers = self.list()
        matches = [cntr for cntr in containers if cntr.name == name]
        if not matches:
            return None
        return matches[0]

    def run(self, image, name, **kwargs):
        """ Launch a docker container (noop if it already exists)

            Return True if launched, else False
        """
        if self.get_container(name):
            return False
        if 'detach' not in kwargs:
            kwargs['detach'] = True
        self.client.containers.run(image, name=name, **kwargs)
        return True

    def execute(self, container_name, cmd, silent=False):
        """ Run docker exec """
        if not silent:
            echo('{}> {}'.format(container_name, cmd))
        container = self.get_container(container_name)
        if not container:
            return {'exit_code': 1, 'output': 'Container not found'}
        exit_code, output = container.exec_run(cmd)
        return {'exit_code': exit_code, 'output': output}

    def export_image(self, image_name, tag=None, force=False):
        """ Save a docker image to a file in directory """
        if tag is None:
            tag = _all_images()[image_name]
        auth = bwdt.lib.auth.get()
        base_dir = auth['offline_path']
        if not os.path.isdir(base_dir):
            echo('ERROR: Directory {} not found'.format(base_dir))
            return
        directory = '{}/images/'.format(base_dir)
        if not os.path.isdir(directory):
            echo('Creating directory: {}'.format(directory))
            os.mkdir(directory)
        path = get_image_as_filename(image_name, tag, directory)
        if offline_image_exists(image_name, tag) and not force:
            echo('WARN: {} already exists: --force to overwrite'.format(path))
            return
        repository = '{}:{}'.format(image_name, tag)
        image = self.client.images.get(repository)
        echo('Saving: {}'.format(path))
        # Do the export and handle errors. A few things might go wrong
        try:
            with open(path, 'wb') as _file:
                for chunk in image.save(named=repository):
                    _file.write(chunk)
        except ReadTimeout:
            # Sometimes Docker will time out trying to export the image
            err = 'Docker timeout trying to export file. Check CPU usage?\n'
            sys.stderr.write('ERROR: {}'.format(err))
        if os.path.exists(path):
            # Worse the ReadTimeout leaves a 0b file behind
            if os.path.getsize(path) == 0:
                sys.stderr.write('WARN: Removing empty file {}\n'.format(path))
                os.remove(path)
            else:
                os.chmod(path, 0o755)
        else:
            sys.stderr.write('ERROR: Failed to create {}\n'.format(path))

    def export_image_all(self, tag=None, force=False):
        """ Pull or import all images """
        all_images = _all_images()
        i = 1
        count = len(all_images)
        for repository in all_images:
            echo('Pulling image {} of {}'.format(i, count))
            i += 1
            self.export_image(image_name=repository, tag=tag, force=force)

    def import_image(self, image_name, tag):
        """ Load a docker image from a file """
        auth = bwdt.lib.auth.get()
        directory = '{}/images/'.format(auth['offline_path'])
        path = get_image_as_filename(image_name, tag, directory)
        echo('Loading {}:{} from {}'.format(image_name, tag, path))
        if not os.path.exists(path):
            sys.stderr.write('ERROR: file {} not found\n'.format(path))
            sys.exit(1)
        with open(path, 'rb') as image:
            self.client.images.load(image)
