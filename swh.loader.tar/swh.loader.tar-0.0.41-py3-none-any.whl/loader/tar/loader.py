# Copyright (C) 2015-2019  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information


import os
import tempfile
import requests
import shutil
from urllib.parse import urlparse

from tempfile import mkdtemp

from swh.core import tarball
from swh.loader.core.loader import BufferedLoader
from swh.loader.dir.loader import revision_from, snapshot_from
from swh.model.hashutil import MultiHash, HASH_BLOCK_SIZE
from swh.model.from_disk import Directory

from .build import compute_revision, set_original_artifact

try:
    from _version import __version__  # type: ignore
except ImportError:
    __version__ = 'devel'


TEMPORARY_DIR_PREFIX_PATTERN = 'swh.loader.tar.'
DEBUG_MODE = '** DEBUG MODE **'


class LocalResponse:
    """Local Response class with iter_content api

    """
    def __init__(self, path):
        self.path = path

    def iter_content(self, chunk_size=None):
        with open(self.path, 'rb') as f:
            for chunk in f:
                yield chunk


class ArchiveFetcher:
    """Http/Local client in charge of downloading archives from a
       remote/local server.

    Args:
        temp_directory (str): Path to the temporary disk location used
                              for downloading the release artifacts

    """
    def __init__(self, temp_directory=None):
        self.temp_directory = temp_directory
        self.session = requests.session()
        self.params = {
            'headers': {
                'User-Agent': 'Software Heritage Tar Loader (%s)' % (
                    __version__
                )
            }
        }

    def download(self, url):
        """Download the remote tarball url locally.

        Args:
            url (str): Url (file or http*)

        Raises:
            ValueError in case of failing to query

        Returns:
            Tuple of local (filepath, hashes of filepath)

        """
        url_parsed = urlparse(url)
        if url_parsed.scheme == 'file':
            path = url_parsed.path
            response = LocalResponse(path)
            length = os.path.getsize(path)
        else:
            response = self.session.get(url, **self.params, stream=True)
            if response.status_code != 200:
                raise ValueError("Fail to query '%s'. Reason: %s" % (
                    url, response.status_code))
            length = int(response.headers['content-length'])

        filepath = os.path.join(self.temp_directory, os.path.basename(url))

        h = MultiHash(length=length)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=HASH_BLOCK_SIZE):
                h.update(chunk)
                f.write(chunk)

        actual_length = os.path.getsize(filepath)
        if length != actual_length:
            raise ValueError('Error when checking size: %s != %s' % (
                length, actual_length))

        hashes = {
            'length': length,
            **h.hexdigest()
        }
        return filepath, hashes


class BaseTarLoader(BufferedLoader):
    """Base Tarball Loader class.

    This factorizes multiple loader implementations:

      - :class:`RemoteTarLoader`: New implementation able to deal with
         remote archives.

      - :class:`TarLoader`: Old implementation which dealt with only
         local archive. It also was only passing along objects to
         persist (revision, etc...)

    """
    CONFIG_BASE_FILENAME = 'loader/tar'

    ADDITIONAL_CONFIG = {
        'working_dir': ('string', '/tmp'),
        'debug': ('bool', False),  # NOT FOR PRODUCTION
    }

    visit_type = 'tar'

    def __init__(self, logging_class='swh.loader.tar.TarLoader', config=None):
        super().__init__(logging_class=logging_class, config=config)
        self.local_cache = None
        self.dir_path = None
        working_dir = self.config.get('working_dir', tempfile.gettempdir())
        os.makedirs(working_dir, exist_ok=True)
        self.temp_directory = mkdtemp(
            suffix='-%s' % os.getpid(),
            prefix=TEMPORARY_DIR_PREFIX_PATTERN,
            dir=working_dir)
        self.client = ArchiveFetcher(temp_directory=self.temp_directory)
        os.makedirs(working_dir, 0o755, exist_ok=True)
        self.dir_path = tempfile.mkdtemp(prefix='swh.loader.tar-',
                                         dir=self.temp_directory)
        self.debug = self.config.get('debug', False)

    def cleanup(self):
        """Clean up temporary disk folders used.

        """
        if self.debug:
            self.log.warn('%s Will not clean up temp dir %s' % (
                DEBUG_MODE, self.temp_directory
            ))
            return
        if os.path.exists(self.temp_directory):
            self.log.debug('Clean up %s' % self.temp_directory)
            shutil.rmtree(self.temp_directory)

    def prepare_origin_visit(self, *, origin, visit_date=None, **kwargs):
        """Prepare the origin visit information.

        Args:
            origin (dict): Dict with keys {url, type}
            visit_date (str): Date representing the date of the
              visit. None by default will make it the current time
              during the loading process.

        """
        self.origin = origin
        if 'type' not in self.origin:  # let the type flow if present
            self.origin['type'] = self.visit_type
        self.visit_date = visit_date

    def get_tarball_url_to_retrieve(self):
        """Compute the tarball url to allow retrieval

        """
        raise NotImplementedError()

    def fetch_data(self):
        """Retrieve, uncompress archive and fetch objects from the tarball.
           The actual ingestion takes place in the :meth:`store_data`
           implementation below.

        """
        url = self.get_tarball_url_to_retrieve()
        filepath, hashes = self.client.download(url)
        nature = tarball.uncompress(filepath, self.dir_path)

        dir_path = self.dir_path.encode('utf-8')
        directory = Directory.from_disk(path=dir_path, save_path=True)
        objects = directory.collect()
        if 'content' not in objects:
            objects['content'] = {}
        if 'directory' not in objects:
            objects['directory'] = {}

        # compute the full revision (with ids)
        revision = self.build_revision(filepath, nature, hashes)
        revision = revision_from(directory.hash, revision)
        objects['revision'] = {
            revision['id']: revision,
        }

        snapshot = self.build_snapshot(revision)
        objects['snapshot'] = {
            snapshot['id']: snapshot
        }
        self.objects = objects

    def store_data(self):
        """Store the objects in the swh archive.

        """
        objects = self.objects
        self.maybe_load_contents(objects['content'].values())
        self.maybe_load_directories(objects['directory'].values())
        self.maybe_load_revisions(objects['revision'].values())
        snapshot = list(objects['snapshot'].values())[0]
        self.maybe_load_snapshot(snapshot)


class RemoteTarLoader(BaseTarLoader):
    """This is able to load from remote/local archive into the swh
       archive.

    This will:

    - create an origin (if it does not exist) and a visit
    - fetch the tarball in a temporary location
    - uncompress it locally in a temporary location
    - process the content of the tarball to persist on swh storage
    - clean up the temporary location

    """
    def prepare(self, *, last_modified, **kwargs):
        """last_modified is the time of last modification of the tarball.

        E.g https://ftp.gnu.org/gnu/8sync/:
            [ ] 8sync-0.1.0.tar.gz	2016-04-22 16:35 	217K
            [ ] 8sync-0.1.0.tar.gz.sig	2016-04-22 16:35 	543
            [ ] ...

        Args:
            origin (dict): Dict with keys {url, type}
            last_modified (str): The date of last modification of the
              archive to ingest.
            visit_date (str): Date representing the date of the
              visit. None by default will make it the current time
              during the loading process.

        """
        self.last_modified = last_modified

    def get_tarball_url_to_retrieve(self):
        return self.origin['url']

    def build_revision(self, filepath, nature, hashes):
        """Build the revision with identifier

        We use the `last_modified` date provided by the caller to
        build the revision.

        """
        return set_original_artifact(
            revision=compute_revision(filepath, self.last_modified),
            filepath=filepath,
            nature=nature,
            hashes=hashes,
        )

    def build_snapshot(self, revision):
        """Build the snapshot targeting the revision.

        """
        branch_name = os.path.basename(self.dir_path)
        return snapshot_from(revision['id'], branch_name)


class LegacyLocalTarLoader(BaseTarLoader):
    """This loads local tarball into the swh archive. It's using the
       revision and branch provided by the caller as scaffolding to
       create the full revision and snapshot (with identifiers).

       This is what's:
       - been used to ingest our 2015 rsync copy of gnu.org
       - still used by the loader deposit

    This will:

    - create an origin (if it does not exist) and a visit
    - uncompress a tarball in a local and temporary location
    - process the content of the tarball to persist on swh storage
    - associate it to a passed revision and snapshot
    - clean up the temporary location

    """
    def prepare(self, *, tar_path, revision, branch_name, **kwargs):
        """Prepare the data prior to ingest it in SWH archive.

        Args:
            tar_path (str): Path to the archive to ingest
            revision (dict): The synthetic revision to associate the
              archive to (no identifiers within)
            branch_name (str): The branch name to use for the
              snapshot.

        """
        self.tar_path = tar_path
        self.revision = revision
        self.branch_name = branch_name

    def get_tarball_url_to_retrieve(self):
        return 'file://%s' % self.tar_path

    def build_revision(self, filepath, nature, hashes):
        """Build the revision with identifier

        We use the revision provided by the caller as a scaffolding
        revision.

        """
        return set_original_artifact(
            revision=self.revision,
            filepath=filepath,
            nature=nature,
            hashes=hashes,
        )

    def build_snapshot(self, revision):
        """Build the snapshot targeting the revision.

        We use the branch_name provided by the caller as a scaffolding
        as well.

        """
        return snapshot_from(revision['id'], self.branch_name)
