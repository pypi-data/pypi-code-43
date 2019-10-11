import logging
from contextlib import contextmanager
from posixpath import join as url_join
import boto3
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session

import smart_open as smart

from emporium.base import AbstractStore
from emporium.utils import select_keys, is_write_mode

log = logging.getLogger(__name__)


class RemoteStoreS3(AbstractStore):
    """Store that puts data on S3."""

    DEFAULT_DOMAIN = "{bucket}.s3-eu-west-1.amazonaws.com"

    def __init__(self, bucket, prefix=None, domain=None, **extra):
        """Instantiate a store.

        :param bucket: The bucket to store data in.
        :param prefix: The prefix within that bucket, under which to store data.
        :param extra: Additional configuration passed to the boto3 session
            constructor.  This might include, ``aws_access_key_id``, ``aws_secret_access_key``
            and ``role_arn``.

        :returns: Instance of a subclass of :class:`~emporium.base.AbstractStore`.
        """

        self._bucket = bucket
        self._prefix = None if not prefix else prefix.lstrip("/")
        self._domain = domain or self.DEFAULT_DOMAIN.format(bucket=bucket)
        self._extra = self._extract_config(extra)

    @classmethod
    def from_config(cls, config):
        return cls(**config)

    @contextmanager
    def open(self, path, mode, *args, **kwargs):
        uri = self._uri(path)
        transport_params = self._create_transport_params()
        transport_params.update(kwargs.get("transport_params", {}))
        if transport_params:
            kwargs["transport_params"] = transport_params
        acl = kwargs.pop("ACL", None)
        with smart.open(uri, mode, *args, **kwargs) as handle:
            yield handle
        if is_write_mode(mode) and acl is not None:
            client = boto3.client("s3")
            key = self._key(path)
            client.put_object_acl(Bucket=self._bucket, Key=key, ACL=acl)

    def substore(self, path):
        subpath = url_join(self._prefix, path.lstrip("/"))
        return RemoteStoreS3(self._bucket, subpath, **self._extra)

    def location(self, path=None):
        segments = [s.lstrip("/") for s in [self._prefix, path] if s]
        if segments:
            return "https://{}/{}".format(self._domain, url_join(*segments))
        return "https://{}".format(self._domain)

    @classmethod
    def _extract_config(cls, extra):
        if not extra:
            return {}
        restriction = ["aws_access_key_id", "aws_secret_access_key", "role_arn"]
        return select_keys(extra, *restriction)

    def _create_transport_params(self):
        if self._extra:
            if "role_arn" in self._extra:
                return {"session": SessionWithAssumedRole(**self._extra).get_session()}
            return {"session": boto3.Session(**self._extra)}
        return {}

    def _key(self, path):
        segments = [s.lstrip("/") for s in [self._prefix, path] if s]
        return url_join(*segments)

    def _uri(self, path=None):
        segments = [s.lstrip("/") for s in [self._bucket, self._prefix, path] if s]
        return "s3://{}".format(url_join(*segments))

    def __repr__(self):
        if self._domain is None:
            return "<{}({})>".format(self.__class__.__name__, self._uri())
        return "<{}({})>".format(self.__class__.__name__, self.location())


class SessionWithAssumedRole:
    def __init__(self, role_arn, **extra):
        self._role_arn = role_arn
        self._session_name = role_arn.split("/")[-1]
        self._extra = self._extract_config(extra)
        self._sts_client = None

    @classmethod
    def _extract_config(cls, extra):
        if not extra:
            return {}
        restriction = ["aws_access_key_id", "aws_secret_access_key"]
        return select_keys(extra, *restriction)

    def get_session(self):
        self._sts_client = boto3.client("sts", **self._extra)
        session_credentials = RefreshableCredentials.create_from_metadata(
            metadata=self._refresh(),
            refresh_using=self._refresh,
            method="sts-assume-role",
        )
        session = get_session()
        # pylint: disable=protected-access
        session._credentials = session_credentials
        autorefresh_session = boto3.Session(botocore_session=session)
        return autorefresh_session

    def _refresh(self):
        log.debug("Refreshing temporary session credentials")
        params = {
            "RoleArn": self._role_arn,
            "RoleSessionName": self._session_name,
            "DurationSeconds": 900,
        }
        response = self._sts_client.assume_role(**params).get("Credentials")
        credentials = {
            "access_key": response.get("AccessKeyId"),
            "secret_key": response.get("SecretAccessKey"),
            "token": response.get("SessionToken"),
            "expiry_time": response.get("Expiration").isoformat(),
        }
        return credentials

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)
