import os

from .base import BaseSSHUploader
from ..exceptions import InvalidUploadDestination, FileAlreadyUploaded


class SSHPypiUploader(BaseSSHUploader):
    uploader_name = 'ssh-pypi'

    def get_destination_path(self, sftp, package_name, file):
        return os.path.join(self.ssh_path, package_name, file.basename)

    def _do_upload_files(self, sftp, package_name, files):
        if not sftp.isdir(os.path.join(self.ssh_path, package_name)):
            raise InvalidUploadDestination(
                'Directory for package `%s`` doesn\'t exist. If this is an error, check if package '
                'didn\'t change. If everything looks fine, contact administrator of this PyPI repository.',
                package_name,
            )
        super()._do_upload_files(sftp, package_name, files)

    def _do_upload_file(self, sftp, package_name, file):
        if sftp.exists(self.get_destination_path(sftp, package_name, file)):
            raise FileAlreadyUploaded(
                'Package %s of version %s (%s) already exists!', package_name, file.version, file.type_display,
            )
        super()._do_upload_file(sftp, package_name, file)
