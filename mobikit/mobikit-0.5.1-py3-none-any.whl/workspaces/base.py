#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

import pandas as pd
import json
from json import JSONDecodeError
import requests
import io
from abc import ABC, abstractmethod
from mobikit_utils.utils import raise_for_types
from mobikit_utils.query_builder.constants import payload_schema, spatial_formats
from mobikit.exceptions import MobikitException
from mobikit.config import config
from mobikit.workspaces.exceptions import (
    FeedError,
    SourceError,
    DBSourceError,
    FileSourceError,
)
from requests.exceptions import RequestException, HTTPError
from mobikit.workspaces.exceptions import PayloadException
from mobikit.workspaces.load.query_builder import Query


class Frameable(ABC):
    @abstractmethod
    def to_df(self):
        """returns a df representation of loaded data"""
        pass


class Loadable(ABC):
    @abstractmethod
    def load(self):
        """loads appropriate source and returns self (for chaining)"""
        pass

    @abstractmethod
    def _handle_request_exception(e, ExceptionClass=MobikitException):
        """gets called whenever a request-realated exception is caught"""
        pass

    def __init__(self, *args, **kwargs):
        self._headers = {"Authorization": "Token {}".format(config.api_token)}
        self._params = {"presigned": "localhost" not in config.base}


class Queryable(Loadable, ABC):
    @abstractmethod
    def query(self, payload):
        """Abstract method to execute db query with provided payload"""
        pass

    def load(self, *args, **kwargs):
        return self.query(*args, **kwargs)

    @classmethod
    def _validate_payload(cls, payload):
        payload = payload or {}
        tmp_key = "query_payload"
        raise_for_types(
            {tmp_key: payload},
            tmp_key,
            allowed_types=[str, dict, Query],
            ExceptionClass=PayloadException,
        )
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except JSONDecodeError as e:
                raise PayloadException("Query payload cannot be parsed as valid JSON")
        elif isinstance(payload, dict):  # type(payload) == dict
            try:
                json.dumps(payload)
            except TypeError as e:
                raise PayloadException("Query payload cannot be parsed as valid JSON")
        else:  # payload is Query
            payload = payload.to_dict()
        payload[payload_schema.meta.name] = {
            payload_schema.meta.spatial_format: spatial_formats.text
        }
        return payload


class BaseSourceRef(Loadable, Frameable, ABC):
    """A reference to a particular data source"""

    def __init__(self, feed_id, source):
        super().__init__(feed_id, source)
        self._feed_id = feed_id
        self._id = source.get("id", None)
        self._name = source.get("name", None)
        self._source = source
        self._view = pd.DataFrame()

    @property
    def name(self):
        return self._source["name"]

    @classmethod
    def create(cls, feed_id, source, **kwargs):
        cls.validate(feed_id, source, **kwargs)
        return cls(feed_id, source, **kwargs)

    @classmethod
    def validate(cls, feed_id, source, **kwargs):
        if not isinstance(feed_id, int):
            raise SourceError(
                f"'feed_id' must be of type <int>. got {type(feed_id)} instead"
            )
        if not isinstance(source, dict):
            raise SourceError(
                f"'source_name' must be of type <str>. got {type(dataset_source_id)} instead"
            )
        # TODO: check for id, resource keys on source, url key on resource

    def _handle_request_exception(self, e, ExceptionClass=MobikitException):
        if isinstance(e, HTTPError):
            res_status = e.response.status_code if e.response is not None else "unknown"
            raise ExceptionClass(
                f"Invalid response status code '{res_status}' recieved when loading source '{self._name}'."
            ) from e
        else:
            raise ExceptionClass(f"Error loading source '{self._name}'.") from e

    @classmethod
    @abstractmethod
    def _parse_response(cls, res):
        """responsible for parsing the raw response from API into view format"""
        pass

    def to_df(self):
        return self._view


class DBSourceRef(BaseSourceRef, Queryable):
    """A reference to a database table source"""

    def __init__(self, feed_id, source):
        super().__init__(feed_id, source)
        self._url = f"{config.query_route}{feed_id}/{self._id}/"

    def load(self):
        return self.query()

    def query(self, payload=None):
        payload = self._validate_payload(payload)

        try:
            res = requests.post(
                self._url, params=self._params, headers=self._headers, json=payload
            )
            res.raise_for_status()
        except RequestException as e:
            config.logger.exception(e)
            self._handle_request_exception(e, ExceptionClass=DBSourceError)
        self._view = self._parse_response(res)
        return self

    @classmethod
    def _parse_response(cls, res):
        res = res.json()
        if res.get("downsized", False):
            downsize_info = res.get("downsize_info", {})
            true_row_count = downsize_info.get("true_count", None)
            config.logger.warn(
                f"WARNING: Your request was very large ({true_row_count} rows), so the query result has been down sized. Please use the query field to narrow your request."
            )
        data = res.get("data")
        if isinstance(data, str):
            data = json.loads(data)
        return pd.DataFrame(data[1:], columns=data[0])


class FileSourceRef(BaseSourceRef):
    """A reference to an S3/CSV file source"""

    def __init__(self, feed_id, source):
        super().__init__(feed_id, source)
        self._url = self._source["resource"]["url"]

    def load(self):
        # try:
        #     res = requests.get(self._url)
        #     res.raise_for_status()
        # except Exception as e:
        #     config.logger.exception(e)
        #     self._handle_request_exception(e, ExceptionClass=FileSourceError)
        self._view = self._parse_response(self._url)
        return self

    @classmethod
    def _parse_response(cls, url):
        return pd.read_csv(url)
        # return pd.read_csv(io.StringIO(res.content.decode("utf-8")))


class FeedRef(Loadable):
    """A reference to a data feed"""

    def __init__(self, feed_id):
        super().__init__()
        self._id = feed_id
        self._sources = []
        self.name = None

    @property
    def id(self):
        return self._id

    @property
    def sources(self):
        return self._sources

    @classmethod
    def create(cls, feed_id):
        cls.validate(feed_id)
        return cls(feed_id)

    @classmethod
    def validate(cls, feed_id):
        if not isinstance(feed_id, int):
            raise FeedError(
                f"'feed_id' must be of type <int>. got {type(feed_id)} instead"
            )

    def _handle_request_exception(self, e, ExceptionClass=FeedError):
        if isinstance(e, HTTPError):
            res_status = e.response.status_code if e.response is not None else "unknown"
            raise ExceptionClass(
                f"Invalid response status code '{res_status}' recieved when loading feed '{self._id}'."
            ) from e
        else:
            raise ExceptionClass(f"Error loading feed '{self._id}'.") from e

    def get_source(self, source_name):
        source = self.sources.get(source_name, None)
        if source is None:
            raise FeedError(
                f"Feed with id: {self._id} does not contain a source with name: {source_name}."
            )
        return source

    def _ref_for_source(self, source, meta_only=False):
        if meta_only:
            return pd.DataFrame()
        if source["resource"]["resource_type"] == "db_table":
            return DBSourceRef.create(self._id, source)
        else:
            return FileSourceRef.create(self._id, source)

    def load(self, meta_only=False):
        try:
            res = requests.get(
                f"{config.feed_route}{self._id}/",
                params=self._params,
                headers=self._headers,
            )
            res.raise_for_status()
        except RequestException as e:
            config.logger.exception(e)
            self._handle_request_exception(e)
        data = json.loads(res.content)
        self.name = data["name"]
        self._sources = {
            source["name"]: self._ref_for_source(source, meta_only=meta_only)
            for source in data["sources"]
        }
        return self
