from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import int
from builtins import str
from builtins import object
from future import standard_library
standard_library.install_aliases()
import binascii
import collections
import datetime
import hashlib
import io
from typing import Any
from typing import Optional
from typing import Union
from six.moves.urllib.parse import quote

from gcloud.rest.auth import BUILD_GCLOUD_REST  # pylint: disable=no-name-in-module
from gcloud.rest.auth import decode  # pylint: disable=no-name-in-module
from gcloud.rest.auth import IamClient  # pylint: disable=no-name-in-module
from gcloud.rest.auth import Token  # pylint: disable=no-name-in-module

# Selectively load libraries based on the package
if BUILD_GCLOUD_REST:
    from requests import Session
else:
    from aiohttp import ClientSession as Session


HOST = 'storage.googleapis.com'


class Blob(object):
    def __init__(self, bucket, name     , metadata      )        :
        self.__dict__.update(**metadata)

        self.bucket = bucket
        self.name = name
        self.size      = int(self.size)

    @property
    def chunk_size(self)       :
        return self.size + (262144 - (self.size % 262144))

    def download(self, session                    = None)       :
        return self.bucket.storage.download(self.bucket.name, self.name,
                                                  session=session)

    def upload(self, data     ,
                     session                    = None)        :
        metadata       = self.bucket.storage.upload(
            self.bucket.name, self.name, data, session=session)

        self.__dict__.update(metadata)
        return metadata

    def get_signed_url(  # pylint: disable=too-many-locals
            self, expiration     , headers                 = None,
            query_params                 = None, http_method      = 'GET',
            iam_client                      = None,
            service_account_email                = None,
            service_file                                  = None,
            token                  = None,
            session                    = None)       :
        """
        Create a temporary access URL for Storage Blob accessible by anyone
        with the link.

        Adapted from Google Documentation:
        https://cloud.google.com/storage/docs/access-control/signing-urls-manually#python-sample
        """
        if expiration > 604800:
            raise ValueError("expiration time can't be longer than 604800 "
                             'seconds (7 days)')

        iam_client = iam_client or IamClient(service_file=service_file,
                                             token=token, session=session)

        quoted_name = quote(self.name, safe='')
        canonical_uri = '/{}/{}'.format((self.bucket.name), (quoted_name))

        datetime_now = datetime.datetime.utcnow()
        request_timestamp = datetime_now.strftime('%Y%m%dT%H%M%SZ')
        datestamp = datetime_now.strftime('%Y%m%d')

        service_account_email = (service_account_email or
                                 iam_client.service_account_email)
        credential_scope = '{}/auto/storage/goog4_request'.format((datestamp))
        credential = '{}/{}'.format((service_account_email), (credential_scope))

        headers = headers or {}
        headers['host'] = HOST

        ordered_headers = collections.OrderedDict(sorted(headers.items()))
        canonical_headers = ''.join(
            '{}:{}\n'.format((str(k).lower()), (str(v).lower()))
            for k, v in ordered_headers.items())

        signed_headers = ';'.join(
            '{}'.format((str(k).lower())) for k in ordered_headers.keys())

        query_params = query_params or {}
        query_params['X-Goog-Algorithm'] = 'GOOG4-RSA-SHA256'
        query_params['X-Goog-Credential'] = credential
        query_params['X-Goog-Date'] = request_timestamp
        query_params['X-Goog-Expires'] = expiration
        query_params['X-Goog-SignedHeaders'] = signed_headers

        ordered_query_params = collections.OrderedDict(
            sorted(query_params.items()))

        canonical_query_str = '&'.join(
            '{}={}'.format((quote(str(k), safe="")), (quote(str(v), safe="")))
            for k, v in ordered_query_params.items())

        canonical_req = '\n'.join([http_method, canonical_uri,
                                   canonical_query_str, canonical_headers,
                                   signed_headers, 'UNSIGNED-PAYLOAD'])
        canonical_req_hash = hashlib.sha256(canonical_req.encode()).hexdigest()

        str_to_sign = '\n'.join(['GOOG4-RSA-SHA256', request_timestamp,
                                 credential_scope, canonical_req_hash])
        signed_resp = iam_client.sign_blob(
            str_to_sign, service_account_email=service_account_email,
            session=session)

        signature = binascii.hexlify(
            decode(signed_resp['signedBlob'])).decode()

        return ('https://{}{}?{}'
                '&X-Goog-Signature={}'.format((HOST), (canonical_uri), (canonical_query_str), (signature)))
