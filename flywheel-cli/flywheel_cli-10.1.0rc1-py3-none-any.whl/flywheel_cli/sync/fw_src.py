import io
import json
import logging
import os
import re
import tempfile
import time
import threading
import zipfile

import dateutil
import flywheel
import requests
from requests_toolbelt.multipart.decoder import MultipartDecoder

from .os_dst import OSDestination


class FWSource:
    """Generator yielding `read()`-able download targets for a ticket"""
    # pylint: disable=too-few-public-methods
    def __init__(self, client, ticket, strip_project=False, unpack=False):
        self.client = client
        self.ticket = ticket
        self.strip_project = strip_project
        self.unpack = unpack

    def __iter__(self):
        response = get_download_targets_response(self.client, self.ticket)
        for part in MultipartDecoder.from_response(response).parts:
            target = json.loads(part.content)
            fwfile = FWFile(self.client, target, strip_project=self.strip_project)
            if self.unpack and fwfile.is_packed:
                # NOTE potential bottleneck when core uses cloud storage (zip seeks)
                for member in fwfile.members:
                    yield member
            else:
                yield fwfile


class FWFile:
    """Enable `read()`-ing download targets"""

    __slots__ = (
        'name', 'size', 'modified', 'bytes_read', 'is_packed',
        'client', 'container_id', 'filename', 'file',
        'unpack_lock', 'unpacked', '_members', '_tempdir'
    )

    def __init__(self, client, target, strip_project=False):
        self.client = client
        self.container_id = target['container_id']
        self.filename = target['filename']
        self.name = target['dst_path'].lstrip('/')
        if strip_project:
            self.name = re.sub(r'^[^/]+/', '', self.name)
        self.modified = dateutil.parser.parse(target['modified']).timestamp()
        if target['download_type'] == 'metadata_sidecar':
            meta = json.dumps(target['metadata']).encode('utf8')
            self.size = len(meta)
            self.file = io.BytesIO(meta)
            self.is_packed = False
        else:
            self.size = target['size']
            self.file = None
            self.is_packed = (target['filetype'] == 'dicom' and
                              target['filename'].lower().endswith('.zip'))
        if self.is_packed:
            self.unpack_lock = threading.Lock()
            self.unpacked = False
            self._members = None
            self._tempdir = None
        self.bytes_read = 0

    def read(self, size=-1):
        """Read `size` bytes from the download target GET response"""
        if self.file is None:
            response = get_container_file_response(self.client, self.container_id, self.filename)
            self.file = response.raw
        data = self.file.read(size)
        if not data:
            self.file.close()
        self.bytes_read += len(data)
        return data

    @property
    def members(self):
        """Return list of DICOM zip members"""
        if self._members is None:
            info = self.client.get_container_file_zip_info(self.container_id, self.filename)
            self._members = [FWMember(self, member) for member in info.members]
        return self._members

    @property
    def tempdir(self):
        """Return path to the downlaoded and extracted DICOM zip"""
        with self.unpack_lock:
            if not self.unpacked:
                self._tempdir = tempfile.TemporaryDirectory()
                filename = os.path.basename(self.name)
                temp = OSDestination(self._tempdir.name).file(filename)
                temp.store(self)
                with zipfile.ZipFile(temp.filepath) as zf:
                    zf.extractall(self._tempdir.name)
                temp.delete()  # slices extracted - remove .zip
                self.unpacked = True
        return self._tempdir.name

    def cleanup(self):
        """Remove the temporary directory of extracted DICOM zip members"""
        if self.is_packed and self.unpacked:
            self._tempdir.cleanup()


class FWMember:
    """Enable `read()`-ing (DICOM) zip members from a locally unpacked FWFile"""
    # pylint: disable=too-few-public-methods

    __slots__ = ('name', 'size', 'modified', 'bytes_read', 'file', 'packfile', 'path')

    def __init__(self, packfile, member):
        self.packfile = packfile
        self.modified = packfile.modified
        self.size = member['size']
        self.path = member['path']
        # NOTE using member basenames instead of full paths (assumes unique names within zip)
        self.name = re.sub(r'\.dicom\.zip$', '/' + os.path.basename(self.path), packfile.name)
        self.file = None
        self.bytes_read = 0

    def read(self, size=-1):
        """Read `size` bytes from the locally unpacked DICOM zip member"""
        if self.file is None:
            filepath = f'{self.packfile.tempdir}/{self.path}'
            self.file = open(filepath, mode='rb')
        data = self.file.read(size)
        self.bytes_read += len(data)
        if not data:
            self.file.close()
        return data

    def cleanup(self):
        """Remove the locally unpacked DICOM slice"""
        if self.packfile.unpacked:
            os.remove(f'{self.packfile.tempdir}/{self.path}')


def retry(func):
    """Decorator for retrying temporary HTTP errors with exponential backoff"""
    def wrapped(*args, **kwargs):
        attempt = 0
        retries = 5
        while True:
            attempt += 1
            retriable = False
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                if isinstance(exc, requests.ConnectionError):
                    # NOTE low-level network issues
                    retriable = True
                if isinstance(exc, requests.HTTPError):
                    # NOTE 429 for google storage rate-limit errors
                    retriable = 500 <= exc.status_code < 600 or exc.status_code == 429
                if isinstance(exc, flywheel.ApiException):
                    # TODO retry functionality in SDK
                    retriable = 500 <= exc.status < 600
                if attempt > retries or not retriable:
                    raise
                time.sleep(2 ** attempt)
    return wrapped


@retry
def get_download_targets_response(client, ticket):
    with LogFilter('urllib3.connectionpool', HeaderParsingErrorFilter):
        response = client.api_client.call_api(
            f'/download/{ticket}/targets', 'GET',
            auth_settings=['ApiKey'],
            _return_http_data_only=True,
            _preload_content=False
        )
    response.raise_for_status()
    return response


@retry
def get_container_file_response(client, container_id, filename):
    response = client.api_client.call_api(
        f'/containers/{container_id}/files/{filename}', 'GET',
        auth_settings=['ApiKey'],
        _return_http_data_only=True,
        _preload_content=False
    )
    response.raise_for_status()
    return response


@retry
def get_container_file_zip_info(client, container_id, filename):
    return client.get_container_file_zip_info(container_id, filename)


class LogFilter:
    """Context manager for temporarily applying logging filters"""
    def __init__(self, logger_name, log_filter):
        self.logger = logging.getLogger(logger_name)
        self.filter = log_filter() if isinstance(log_filter, type) else log_filter

    def __enter__(self):
        self.logger.addFilter(self.filter)

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.removeFilter(self.filter)


class HeaderParsingErrorFilter(logging.Filter):
    """Filter urllib3.exceptions.HeaderParsingError warnings mistakenly emitted
    for multipart responses. See also: https://stackoverflow.com/q/49338811"""
    # pylint: disable=too-few-public-methods
    def filter(self, record):
        return 'Failed to parse headers' not in record.getMessage()
