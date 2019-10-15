import os
import uuid
import zipfile
import shutil

from lxml import etree


class DarException(Exception):
    pass


class MetadataError(DarException):
    pass


class DarFileNotFound(DarException):
    pass


class Manifest:

    def __init__(self, manifest):
        """
        param manifest: XML following .dar manifest template
        """
        self._manifest = manifest
        self.parsed_manifest = self.parse()

    def parse(self):
        return etree.fromstring(self._manifest)

    @property
    def article_path(self):

        try:
            return self.parsed_manifest.find('documents/document[@type="article"]').get('path')
        except AttributeError:
            raise MetadataError('Manifest without document element with @type="article"')

    @property
    def documents(self):

        documents = []
        for document in self.parsed_manifest.xpath('//document'):
            documents.append(document.attrib)

        return documents

    @property
    def assets(self):

        assets = []
        for asset in self.parsed_manifest.xpath('//asset'):
            assets.append(asset.attrib)

        return assets


class DarFileHandler:

    """Manage .dar assets in a temporary directory by the use of context manager"""

    def __init__(self, source):
        self._temp_dir_code = str(uuid.uuid4())
        self._darfile = source.replace('\\', '/')

    @property
    def darfile_directory(self):
        darfile_directory = self._darfile.split('/')[0:-1]
        return '/'.join(darfile_directory)

    @property
    def temp_directory(self):
        return '/'.join([self.darfile_directory, self._temp_dir_code])

    @property
    def temp_article_path(self):
        return '/'.join([self.darfile_directory, self._temp_dir_code, self.manifest.article_path])

    def get_assets(self):
        for asset in self.manifest.assets:
            asset = asset.get('path')
            if asset is None:
                continue
            from_asset = '/'.join([self.temp_directory, asset])
            to_asset = '/'.join([self.darfile_directory, asset])
            shutil.copyfile(from_asset, to_asset)

    @property
    def manifest(self):
        manifest = '/'.join([self.temp_directory, 'manifest.xml'])
        with open(manifest, 'rb') as man:
            manifest = man.read()

        return Manifest(manifest)

    def __enter__(self):
        os.mkdir(self.temp_directory)
        try:
            zipfile.ZipFile(self._darfile).extractall(path=self.temp_directory)
        except FileNotFoundError:
            self.__exit__()
            raise DarFileNotFound('File not found: %s' % self._darfile)

        return self

    def __exit__(self, *args):
        shutil.rmtree(self.temp_directory)
