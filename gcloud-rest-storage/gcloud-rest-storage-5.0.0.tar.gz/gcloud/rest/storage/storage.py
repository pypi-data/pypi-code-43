from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import range
from builtins import str
from builtins import object
from future import standard_library
standard_library.install_aliases()
import enum
import io
import logging
import mimetypes
import os
from typing import Any
from typing import Optional
from typing import Tuple
from typing import Union
from six.moves.urllib.parse import quote

from gcloud.rest.auth import SyncSession  # pylint: disable=no-name-in-module
from gcloud.rest.auth import BUILD_GCLOUD_REST  # pylint: disable=no-name-in-module
from gcloud.rest.auth import Token  # pylint: disable=no-name-in-module
from gcloud.rest.storage.bucket import Bucket

try:
    import ujson as json
except ImportError:
    import json  # type: ignore

# Selectively load libraries based on the package
if BUILD_GCLOUD_REST:
    from time import sleep
    from requests import HTTPError as ResponseError
    from requests import Session
else:
    from asyncio import sleep
    from aiohttp import ClientResponseError as ResponseError
    from aiohttp import ClientSession as Session

API_ROOT = 'https://www.googleapis.com/storage/v1/b'
API_ROOT_UPLOAD = 'https://www.googleapis.com/upload/storage/v1/b'
SCOPES = [
    'https://www.googleapis.com/auth/devstorage.read_write',
]

MAX_CONTENT_LENGTH_SIMPLE_UPLOAD = 5 * 1024 * 1024  # 5 MB


log = logging.getLogger(__name__)


class UploadType(enum.Enum):
    SIMPLE = 1
    RESUMABLE = 2


class Storage(object):
    def __init__(self, **_3to2kwargs)        :
        if 'session' in _3to2kwargs: session = _3to2kwargs['session']; del _3to2kwargs['session']
        else: session =  None
        if 'token' in _3to2kwargs: token = _3to2kwargs['token']; del _3to2kwargs['token']
        else: token =  None
        if 'service_file' in _3to2kwargs: service_file = _3to2kwargs['service_file']; del _3to2kwargs['service_file']
        else: service_file =  None
        self.session = SyncSession(session)
        self.token = token or Token(service_file=service_file, scopes=SCOPES,
                                    session=self.session.session)

    def get_bucket(self, bucket_name     )          :
        return Bucket(self, bucket_name)

    def delete(self, bucket     , object_name     , **_3to2kwargs)       :
        if 'session' in _3to2kwargs: session = _3to2kwargs['session']; del _3to2kwargs['session']
        else: session =  None
        if 'timeout' in _3to2kwargs: timeout = _3to2kwargs['timeout']; del _3to2kwargs['timeout']
        else: timeout =  10
        if 'params' in _3to2kwargs: params = _3to2kwargs['params']; del _3to2kwargs['params']
        else: params =  None
        token = self.token.get()
        # https://cloud.google.com/storage/docs/json_api/#encoding
        encoded_object_name = quote(object_name, safe='')
        url = '{}/{}/o/{}'.format((API_ROOT), (bucket), (encoded_object_name))
        headers = {
            'Authorization': 'Bearer {}'.format((token)),
        }

        s = SyncSession(session) if session else self.session
        resp = s.delete(url, headers=headers, params=params or {},
                              timeout=timeout)

        try:
            data      = resp.text()
        except (AttributeError, TypeError):
            data      = str(resp.text)

        return data

    def download(self, bucket     , object_name     , **_3to2kwargs)         :
        if 'session' in _3to2kwargs: session = _3to2kwargs['session']; del _3to2kwargs['session']
        else: session =  None
        if 'timeout' in _3to2kwargs: timeout = _3to2kwargs['timeout']; del _3to2kwargs['timeout']
        else: timeout =  10
        return self._download(bucket, object_name, timeout=timeout,
                                    params={'alt': 'media'}, session=session)

    def download_metadata(self, bucket     , object_name     , **_3to2kwargs)        :
        if 'session' in _3to2kwargs: session = _3to2kwargs['session']; del _3to2kwargs['session']
        else: session =  None
        if 'timeout' in _3to2kwargs: timeout = _3to2kwargs['timeout']; del _3to2kwargs['timeout']
        else: timeout =  10
        data = self._download(bucket, object_name, timeout=timeout,
                                    session=session)
        metadata       = json.loads(data.decode())
        return metadata

    def list_objects(self, bucket     , **_3to2kwargs)        :
        if 'timeout' in _3to2kwargs: timeout = _3to2kwargs['timeout']; del _3to2kwargs['timeout']
        else: timeout =  10
        if 'session' in _3to2kwargs: session = _3to2kwargs['session']; del _3to2kwargs['session']
        else: session =  None
        if 'params' in _3to2kwargs: params = _3to2kwargs['params']; del _3to2kwargs['params']
        else: params =  None
        token = self.token.get()
        url = '{}/{}/o'.format((API_ROOT), (bucket))
        headers = {
            'Authorization': 'Bearer {}'.format((token)),
        }

        s = SyncSession(session) if session else self.session
        resp = s.get(url, headers=headers, params=params or {},
                           timeout=timeout)
        data       = resp.json()
        return data

    # TODO: if `metadata` is set, use multipart upload:
    # https://cloud.google.com/storage/docs/json_api/v1/how-tos/upload
    # pylint: disable=too-many-locals
    def upload(self, bucket     , object_name     , file_data     , **_3to2kwargs)        :
        if 'force_resumable_upload' in _3to2kwargs: force_resumable_upload = _3to2kwargs['force_resumable_upload']; del _3to2kwargs['force_resumable_upload']
        else: force_resumable_upload =  None
        if 'timeout' in _3to2kwargs: timeout = _3to2kwargs['timeout']; del _3to2kwargs['timeout']
        else: timeout =  30
        if 'session' in _3to2kwargs: session = _3to2kwargs['session']; del _3to2kwargs['session']
        else: session =  None
        if 'metadata' in _3to2kwargs: metadata = _3to2kwargs['metadata']; del _3to2kwargs['metadata']
        else: metadata =  None
        if 'headers' in _3to2kwargs: headers = _3to2kwargs['headers']; del _3to2kwargs['headers']
        else: headers =  None
        if 'parameters' in _3to2kwargs: parameters = _3to2kwargs['parameters']; del _3to2kwargs['parameters']
        else: parameters =  None
        if 'content_type' in _3to2kwargs: content_type = _3to2kwargs['content_type']; del _3to2kwargs['content_type']
        else: content_type =  None
        token = self.token.get()
        url = '{}/{}/o'.format((API_ROOT_UPLOAD), (bucket))

        stream = self._preprocess_data(file_data)

        if BUILD_GCLOUD_REST and isinstance(stream, io.StringIO):
            # HACK: `requests` library does not accept `str` as `data` in `put`
            # HTTP request.
            stream = io.BytesIO(stream.getvalue().encode('utf-8'))

        content_length = self._get_stream_len(stream)

        # mime detection method same as in aiohttp 3.4.4
        content_type = content_type or mimetypes.guess_type(object_name)[0]

        parameters = parameters or {}

        headers = headers or {}
        headers.update({
            'Authorization': 'Bearer {}'.format((token)),
            'Content-Length': str(content_length),
            'Content-Type': content_type or '',
        })

        upload_type = self._decide_upload_type(force_resumable_upload,
                                               content_length)
        log.debug('using %r gcloud storage upload method', upload_type)

        if upload_type == UploadType.SIMPLE:
            if metadata:
                log.warning('metadata will be ignored for upload_type=Simple')
            return self._upload_simple(url, object_name, stream,
                                             parameters, headers,
                                             session=session, timeout=timeout)

        if upload_type == UploadType.RESUMABLE:
            return self._upload_resumable(
                url, object_name, stream, parameters, headers,
                metadata=metadata, session=session, timeout=timeout)

        raise TypeError('upload type {} not supported'.format((upload_type)))

    @staticmethod
    def _get_stream_len(stream           )       :
        current = stream.tell()
        try:
            return stream.seek(0, os.SEEK_END)
        finally:
            stream.seek(current)

    @staticmethod
    def _preprocess_data(data     )             :
        if data is None:
            return io.StringIO('')

        if isinstance(data, bytes):
            return io.BytesIO(data)
        if isinstance(data, str):
            return io.StringIO(data)
        if isinstance(data, io.IOBase):
            return data

        raise TypeError('unsupported upload type: "{}"'.format((type(data))))

    @staticmethod
    def _decide_upload_type(force_resumable_upload                ,
                            content_length     )              :
        # force resumable
        if force_resumable_upload is True:
            return UploadType.RESUMABLE

        # force simple
        if force_resumable_upload is False:
            return UploadType.SIMPLE

        # decide based on Content-Length
        if content_length > MAX_CONTENT_LENGTH_SIMPLE_UPLOAD:
            return UploadType.RESUMABLE

        return UploadType.SIMPLE

    @staticmethod
    def _split_content_type(content_type     )                   :
        content_type_and_encoding_split = content_type.split(';')
        content_type = content_type_and_encoding_split[0].lower().strip()

        encoding = None
        if len(content_type_and_encoding_split) > 1:
            encoding_str = content_type_and_encoding_split[1].lower().strip()
            encoding = encoding_str.split('=')[-1]

        return content_type, encoding

    def _download(self, bucket     , object_name     , **_3to2kwargs)         :
        if 'session' in _3to2kwargs: session = _3to2kwargs['session']; del _3to2kwargs['session']
        else: session =  None
        if 'timeout' in _3to2kwargs: timeout = _3to2kwargs['timeout']; del _3to2kwargs['timeout']
        else: timeout =  10
        if 'params' in _3to2kwargs: params = _3to2kwargs['params']; del _3to2kwargs['params']
        else: params =  None
        token = self.token.get()
        # https://cloud.google.com/storage/docs/json_api/#encoding
        encoded_object_name = quote(object_name, safe='')
        url = '{}/{}/o/{}'.format((API_ROOT), (bucket), (encoded_object_name))
        headers = {
            'Authorization': 'Bearer {}'.format((token)),
        }

        s = SyncSession(session) if session else self.session
        response = s.get(url, headers=headers, params=params or {},
                               timeout=timeout)
        # N.B. the GCS API sometimes returns 'application/octet-stream' when a
        # string was uploaded. To avoid potential weirdness, always return a
        # bytes object.
        try:
            data        = response.read()
        except (AttributeError, TypeError):
            data        = response.content

        return data

    def _upload_simple(self, url     , object_name     ,
                             stream           , params      , headers      , **_3to2kwargs)        :
        # https://cloud.google.com/storage/docs/json_api/v1/how-tos/simple-upload
        if 'timeout' in _3to2kwargs: timeout = _3to2kwargs['timeout']; del _3to2kwargs['timeout']
        else: timeout =  30
        if 'session' in _3to2kwargs: session = _3to2kwargs['session']; del _3to2kwargs['session']
        else: session =  None
        params['name'] = object_name
        params['uploadType'] = 'media'

        headers.update({
            'Accept': 'application/json',
        })

        s = SyncSession(session) if session else self.session
        resp = s.post(url, data=stream, headers=headers, params=params,
                            timeout=timeout)
        data       = resp.json()
        return data

    def _upload_resumable(self, url     , object_name     ,
                                stream           , params      ,
                                headers      , **_3to2kwargs)        :
        # https://cloud.google.com/storage/docs/json_api/v1/how-tos/resumable-upload
        if 'timeout' in _3to2kwargs: timeout = _3to2kwargs['timeout']; del _3to2kwargs['timeout']
        else: timeout =  30
        if 'session' in _3to2kwargs: session = _3to2kwargs['session']; del _3to2kwargs['session']
        else: session =  None
        if 'metadata' in _3to2kwargs: metadata = _3to2kwargs['metadata']; del _3to2kwargs['metadata']
        else: metadata =  None
        session_uri = self._initiate_upload(url, object_name, params,
                                                  headers, metadata=metadata,
                                                  session=session)
        data       = self._do_upload(session_uri, stream,
                                           headers=headers, session=session,
                                           timeout=timeout)
        return data

    def _initiate_upload(self, url     , object_name     , params      ,
                               headers      , **_3to2kwargs)       :
        if 'session' in _3to2kwargs: session = _3to2kwargs['session']; del _3to2kwargs['session']
        else: session =  None
        if 'metadata' in _3to2kwargs: metadata = _3to2kwargs['metadata']; del _3to2kwargs['metadata']
        else: metadata =  None
        params['uploadType'] = 'resumable'

        metadict = (metadata or {}).copy()
        metadict.update({'name': object_name})
        metadata = json.dumps(metadict)

        post_headers = headers.copy()
        post_headers.update({
            'Content-Length': str(len(metadata)),
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Upload-Content-Type': headers['Content-Type'],
            'X-Upload-Content-Length': headers['Content-Length']
        })

        s = SyncSession(session) if session else self.session
        resp = s.post(url, headers=post_headers, params=params,
                            data=metadata, timeout=10)
        session_uri      = resp.headers['Location']
        return session_uri

    def _do_upload(self, session_uri     , stream           ,
                         headers      , **_3to2kwargs)        :
        if 'timeout' in _3to2kwargs: timeout = _3to2kwargs['timeout']; del _3to2kwargs['timeout']
        else: timeout =  30
        if 'session' in _3to2kwargs: session = _3to2kwargs['session']; del _3to2kwargs['session']
        else: session =  None
        if 'retries' in _3to2kwargs: retries = _3to2kwargs['retries']; del _3to2kwargs['retries']
        else: retries =  5
        s = SyncSession(session) if session else self.session

        for tries in range(retries):
            try:
                resp = s.put(session_uri, headers=headers,
                                   data=stream, timeout=timeout)
            except ResponseError:
                headers.update({'Content-Range': '*/*'})
                sleep(2. ** tries)

                continue

            break

        data       = resp.json()
        return data
