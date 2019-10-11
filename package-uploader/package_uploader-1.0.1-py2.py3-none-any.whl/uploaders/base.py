import os
from collections import OrderedDict

import paramiko
import pysftp
import yaml
from paramiko import RSAKey, DSSKey, ECDSAKey, Ed25519Key, SSHException

from ..exceptions import UploadError


class OrderedLoader(yaml.SafeLoader):
    pass


def construct_mapping(loader, node):
    loader.flatten_mapping(node)
    return OrderedDict(loader.construct_pairs(node))


OrderedLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_mapping
)


class UploaderRegistry:

    def __init__(self, config_file="~/.package_uploader.yml"):
        self.config_file = config_file
        self._repos = None
        self.registered_uploaders = {}

    def get_uploader_class(self, service):
        return self.registered_uploaders[service]


class UploaderMetaclass(type):
    def __new__(mcs, name, bases, class_dict):
        cls = super().__new__(mcs, name, bases, class_dict)
        if not len(bases):
            cls.registry = UploaderRegistry()
            mcs._base = cls
        if not class_dict.get('abstract', False):
            registered_name = class_dict['uploader_name']
            mcs._base.registry.registered_uploaders[registered_name] = cls
        else:
            cls.abstract = False
        return cls


class BaseUploader(metaclass=UploaderMetaclass):
    abstract = True

    def __init__(self, location, auth):
        if self.abstract:
            raise TypeError('Abstract uploaders are not meant to be used directly. Subclass this uploader instead.')
        self.location = location
        self.auth = auth


class BaseSSHUploader(BaseUploader):
    abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssh_host = self.location['host']
        self.ssh_port = self.location.get('port', 22)
        self.ssh_user = self.location.get('user')
        self.ssh_path = self.location.get('path', '~')

    def get_ssh_key(self):
        if self.auth is None or 'ssh_key' not in self.auth:
            return None

        key_path = self.auth['ssh_key']

        if key_path.startswith('@agent'):
            agent = paramiko.Agent()
            keys = agent.get_keys()

            key_no = int(key_path.replace('@agent', '').replace('.', '').replace('[', '').replace(']', '') or 0)

            return keys[key_no] if key_no < len(keys) else None

        password = self.auth.get('ssh_key_password')

        for pkey_class in (RSAKey, DSSKey, ECDSAKey, Ed25519Key):
            try:
                key = pkey_class.from_private_key_file(key_path, password)
            except SSHException as e:
                continue
            else:
                return key
        return key_path  # If cannot be treated as any key type, try pass filename to paramiko, maybe it will figure out

    def get_destination_path(self, sftp, package_name, file):
        raise NotImplementedError('`change_to_upload_dir` must be subclassed for any subclass of `BaseSSHUploader`')

    def _do_upload_files(self, sftp, package_name, files):
        """
        Does actual upload of files, after SFTP connection has been estabilished. Can be subclassed to add additional
        checks or other actions that have to be performed on remote host before uploading (i.e. checking if destination
        directory exist and, if necessary, creating it). If files shouldn't be uploaded at all, an exception should be
        thrown.
        :param sftp: sftp connection
        :param package_name: normalized name of the package that is being uploaded
        :param files: package files to be uploaded
        """
        for file in files:
            self._do_upload_file(sftp, package_name, file)

    def _do_upload_file(self, sftp, package_name, file):
        """
        Does actual upload of single file. This can be subclassed to add additional checks if this particular file can
        be uploaded or should be skipped. It should throw an exception if upload process should be stopped as a whole or
        should just skip actual uploading of the file (for example by not calling super) if only single file should be skipped
        :param sftp: sftp connection
        :param package_name: nomralized name of the package that is being uploaded
        :param file: package file that is being uploaded
        """
        sftp.put(file.path, remotepath=self.get_destination_path(sftp, package_name, file))

    def upload_files(self, package_name, files):
        key = self.get_ssh_key()
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys.load('/etc/ssh/ssh_known_hosts')
        with pysftp.Connection(host=self.ssh_host, username=self.ssh_user, private_key=key, cnopts=cnopts) as sftp:
            self._do_upload_files(sftp, package_name, files)
