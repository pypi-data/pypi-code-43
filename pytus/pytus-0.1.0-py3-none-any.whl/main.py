import base64
import logging
import os
from urllib.parse import urlparse, urlunparse

import requests

LOG_LEVEL = logging.INFO
DEFAULT_CHUNK_SIZE = 4 * 1024 * 1024
TUS_VERSION = '1.0.0'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.NullHandler())


class TusError(Exception):
    def __init__(self, message, response=None):
        super(TusError, self).__init__(message)
        self.response = response
        self._message = message

    def __str__(self):
        if self.response is not None:
            text = self.response.text
            return f"TusError('{self._message}', response=({self.response.status_code}, '{text.strip()}'))"
        else:
            return f"TusError('{self._message}')"


def _init():
    fmt = "[%(asctime)s] %(levelname)s %(message)s"
    h = logging.StreamHandler()
    h.setLevel(LOG_LEVEL)
    h.setFormatter(logging.Formatter(fmt))
    logger.addHandler(h)


def upload(file_obj,
           tus_endpoint,
           chunk_size=DEFAULT_CHUNK_SIZE,
           file_name=None,
           headers=None,
           session=None,
           metadata=None):

    file_name = file_name or os.path.basename(file_obj.name)
    file_size = _get_file_size(file_obj)

    if not session:
        session = requests

    file_endpoint = create(
        tus_endpoint,
        file_name,
        file_size,
        session,
        headers=headers,
        metadata=metadata)

    resume(
        file_obj,
        file_endpoint,
        session,
        chunk_size=chunk_size,
        headers=headers,
        offset=0)


def _get_file_size(f):
    if not f.seekable():
        return

    pos = f.tell()
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(pos)
    return size


def _absolute_file_location(tus_endpoint, file_endpoint):
    parsed_file_endpoint = urlparse(file_endpoint)
    if parsed_file_endpoint.netloc:
        return file_endpoint

    parsed_tus_endpoint = urlparse(tus_endpoint)
    return urlunparse((
        parsed_tus_endpoint.scheme,
        parsed_tus_endpoint.netloc,
    ) + parsed_file_endpoint[2:])


def create(tus_endpoint, file_name, file_size, session, headers=None, metadata=None):
    logger.info("Creating file endpoint")

    h = {"Tus-Resumable": TUS_VERSION}

    if file_size is None:
        h['Upload-Defer-Length'] = '1'
    else:
        h['Upload-Length'] = str(file_size)

    if headers:
        h.update(headers)

    if metadata is None:
        metadata = {}

    metadata['filename'] = file_name

    pairs = [
        k + ' ' + base64.b64encode(v.encode('utf-8')).decode()
        for k, v in metadata.items()
    ]
    h["Upload-Metadata"] = ','.join(pairs)

    response = session.post(tus_endpoint, headers=h)
    if response.status_code != 201:
        raise TusError("Create failed", response=response)

    location = response.headers["Location"]
    logger.info(f"Created: {location}")
    return _absolute_file_location(tus_endpoint, location)


def resume(file_obj,
           file_endpoint,
           session,
           chunk_size=DEFAULT_CHUNK_SIZE,
           headers=None,
           offset=None):

    if offset is None:
        offset = _get_offset(file_endpoint, session, headers=headers)

    if offset != 0:
        if not file_obj.seekable():
            raise Exception("file is not seekable")

        file_obj.seek(offset)

    total_sent = 0
    data = file_obj.read(chunk_size)
    while data:
        _upload_chunk(data, offset, file_endpoint, session, headers=headers)
        total_sent += len(data)
        logger.info(f"Total bytes sent: {total_sent}")
        offset += len(data)
        data = file_obj.read(chunk_size)

    if not file_obj.seekable():
        if headers is None:
            headers = {}
        else:
            headers = dict(headers)

        headers['Upload-Length'] = str(offset)
        _upload_chunk('', offset, file_endpoint, session, headers=headers)


def _get_offset(file_endpoint, session, headers=None):
    logger.info("Getting offset")

    h = {"Tus-Resumable": TUS_VERSION}

    if headers:
        h.update(headers)

    response = session.head(file_endpoint, headers=h)
    response.raise_for_status()

    offset = int(response.headers["Upload-Offset"])
    logger.info(f"offset={offset}")
    return offset


def _upload_chunk(data, offset, file_endpoint, session, headers=None):
    logger.info(f"Uploading {len(data)} bytes chunk from offset: {offset}")

    h = {
        'Content-Type': 'application/offset+octet-stream',
        'Upload-Offset': str(offset),
        'Tus-Resumable': TUS_VERSION,
    }

    if headers:
        h.update(headers)

    response = session.patch(file_endpoint, headers=h, data=data)
    if response.status_code != 204:
        raise TusError("Upload chunk failed", response=response)
