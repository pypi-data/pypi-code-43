import os
import hashlib
import tempfile

from bamboo_lib.logger import logger
from bamboo_lib.connectors.models import BaseDriver
from bamboo_lib.helpers import decrypt, process_uri_wildcards, wildcard_matches
from bamboo_lib.exceptions import InvalidCredentialsException
from google.cloud import storage

from urllib.parse import urlparse

class GCSDriver(BaseDriver):
    TYPE = 'Google Cloud Storage Driver'

    def __init__(self, credentials_path=None, credentials_string=None,
            force=None, 
            delimiter="/",
            **kwargs):
        self.timeout = kwargs.get("timeout", None)
        self.force = force
        self.delimiter = delimiter
        super().__init__(**kwargs)
        self.credentials_path = credentials_path
        self.credentials_string = credentials_string
        self.is_encrypted = kwargs.get("is_encrypted", False)
        if self.credentials_path:
            self._client = storage.Client.from_service_account_json(self.credentials_path)
        elif self.credentials_string:
            raw_credentials_str = self.credentials_string
            with tempfile.NamedTemporaryFile(delete=True) as fp:
                if kwargs.get("is_encrypted", False):
                    env_var_name = kwargs.get("secret_env_var", "BAMBOO_SECRET")
                    my_passcode = os.environ.get(env_var_name, None)
                    if not my_passcode:
                        raise ValueError("""GCS connector is_encrypted is set to true 
                            but could not read a value for environment variable: {}""".format(env_var_name))
                    raw_credentials_str = decrypt(raw_credentials_str, my_passcode).decode("utf-8")
                fp.write(raw_credentials_str.encode("utf-8"))
                fp.seek(0)
                self._client = storage.Client.from_service_account_json(fp.name)
        elif os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", None):
            self._client = storage.Client()
        else:
            raise InvalidCredentialsException("You must either set GOOGLE_APPLICATION_CREDENTIALS environment variable OR credentials_path in connector configuration")

    def serialize(self):
        return {
            "timeout": self.timeout,
            "force": self.force,
            "credentials_path": self.credentials_path,
            "credentials_string": self.credentials_string,
            "is_encrypted": self.is_encrypted,
            "delimiter": self.delimiter
        }

    @classmethod
    def deserialize(cls, kwargs):
        return cls(**kwargs)


    @staticmethod
    def uri_to_components(gs_uri_str):
        parsed_info = urlparse(gs_uri_str)
        bucket_name = parsed_info.netloc
        path = parsed_info.path[1:] if parsed_info.path and parsed_info.path.startswith("/") else parsed_info.path
        return bucket_name, path

    def download(self, params=None, http_params=None, force=False, callback=None):
        """Downloads a blob from a Google Cloud Storage bucket."""
        uri = BaseDriver.resolve_params(self.uri, params)
        bucket_name, source_path = self.uri_to_components(uri)
        download_path = GCSDriver.get_download_path()
        local_filename = os.path.join(download_path, hashlib.sha224(uri.encode("utf-8")).hexdigest())
        logger.info("Downloading GCS resource: {} ...".format(uri))
        # if already downloaded, dont re-download unless required
        if not force and not self.force and os.path.isfile(local_filename):
            logger.info("Reading web asset from local cache...")
            return local_filename
        bucket = self._client.get_bucket(bucket_name)
        blob = bucket.blob(source_path)
        blob.download_to_filename(local_filename)
        logger.info('Blob {} downloaded to {}.'.format(
            source_path,
            local_filename))
        return local_filename


    def download_single(self, uri, params=None, http_params=None, force=False, callback=None):
        """Downloads a blob from a Google Cloud Storage bucket."""
        bucket_name, source_path = self.uri_to_components(uri)
        download_path = GCSDriver.get_download_path()
        local_filename = os.path.join(download_path, hashlib.sha224(uri.encode("utf-8")).hexdigest())
        logger.info("Downloading GCS resource: {} ...".format(uri))
        # if already downloaded, dont re-download unless required
        if not force and not self.force and os.path.isfile(local_filename):
            logger.info("Reading web asset from local cache...")
            return local_filename
        bucket = self._client.get_bucket(bucket_name)
        blob = bucket.blob(source_path)
        blob.download_to_filename(local_filename)
        logger.info('Blob {} downloaded to {}.'.format(
            source_path,
            local_filename))
        return local_filename


    @staticmethod
    def gcs_uri(bucket, blob_name):
        return "gs://{}/{}".format(bucket, blob_name)

    def get_targets(self, params=None):
        uri = BaseDriver.resolve_params(self.uri, params)
        bucket_name, _ = self.uri_to_components(uri)
        blobs = self._client.list_blobs(bucket_name)
        blob_strs = [self.gcs_uri(bucket_name, b.name) for b in blobs]
        uri_pattern = process_uri_wildcards(uri)
        results = []
        for uri_to_test in blob_strs:
            matches = wildcard_matches(uri_pattern, uri_to_test)
            if matches:
                results.append((uri_to_test, matches))
        return results

