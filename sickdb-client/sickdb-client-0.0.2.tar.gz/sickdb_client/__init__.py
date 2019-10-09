"""
A comprehensize python client for the SickDB API.
"""

import os
import json

import requests
from requests import Session, Request
from requests.exceptions import ConnectionError

# python 2 -> 3
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

RET_CODES = [200, 201, 202]
GOOD_CODES = RET_CODES + [204]


class ClientError(Exception):
    pass


class BaseClient(object):

    """
    A base client for each endpoint to inherit from.
    """

    def __init__(self, **kw):

        # defaults / helpers
        self.api_key = kw.get("api_key", os.getenv("SICKDB_API_KEY"))
        self.url = kw.pop("url", os.getenv("SICKDB_API_URL", "http://localhost:3030"))
        self.raise_errors = kw.get("raise_errors", False)

        # standardize url
        if self.url.endswith("/"):
            self.url = self.url[:-1]

        # establish session
        self.session = Session()

    def format_url(self, *args):
        """
        Add segments to endpoint to form a URL.
        """

        return urljoin(self.url, "/".join([str(a) for a in args]))

    def request(self, method, url, **kwargs):
        """
        A wrapper for all request executions.
        """

        if not self.api_key:
            raise ClientError("You haven't set your api_key!")

        # issue request.
        err = None
        resp = None
        try:
            r = Request(method, url, **kwargs)
            resp = self.session.send(r.prepare())

        except ConnectionError as e:
            err = ClientError(
                "Could not connect to {0} beacuse: {1}".format(self.url, e)
            )

        # handle errors
        return self._handle_response(resp, err)

    def prepare_request_kwargs(self, raw, params=[], json=True):
        """
        Allow POST/PUT methods to accept an undifferentiated list of kwargs.
        This function will separate them into query parameters, data, and files
        so we can initalize the Request object properly.
        """

        # defaults
        prepared_kwargs = {"params": {"api_key": self.api_key}}

        # always include in params
        if "api_key" in raw:
            api_key = raw.pop("api_key")
            prepared_kwargs["params"]["api_key"] = api_key
            self.api_key = api_key

        # include in params
        for p in params:
            if p in raw:
                prepared_kwargs["params"][p] = raw.pop(p)

        # separate out file from data
        if "file" in raw:
            prepared_kwargs["files"] = {"file": raw.pop("file")}

        # if we have anything else...
        if len(raw.keys()):
            # if everything should be parameters...
            if not json:
                prepared_kwargs["params"].update(raw)

            # otherwise it's POST/PUT data
            else:
                prepared_kwargs["json"] = raw

        return prepared_kwargs

    def _handle_response(self, resp, err):
        """
        Handle all errors + format response.
        """
        # check for connection errors
        if not resp and err:
            raise err

        if resp.status_code not in GOOD_CODES:
            if self.raise_errors:
                d = resp.json()
                raise ClientError(d["message"])

        # just return the response and let the client handle
        # json parsing etc
        return resp


class CollectionClient(BaseClient):
    """
    An abstract client for simple collections
    """

    def __init__(self, *args, **kwargs):
        _name = kwargs.pop("name")
        BaseClient.__init__(self, *args, **kwargs)
        self.name = _name

    def search(self, **kw):
        """
        Search a collection
        """
        kwargs = self.prepare_request_kwargs(kw, json=False)
        url = self.format_url("/{0}/".format(self.name))
        return self.request("GET", url, **kwargs)

    def create(self, **kw):
        """
        Create a instance of a collection
        """
        kwargs = self.prepare_request_kwargs(kw)
        url = self.format_url("/{0}/".format(self.name))
        return self.request("POST", url, **kwargs)

    def get(self, id, **kw):
        """
        Fetch an instance of a collection
        """
        kwargs = self.prepare_request_kwargs(kw, json=False)
        url = self.format_url("/{0}/{1}".format(self.name, id))
        return self.request("GET", url, **kwargs)

    def update(self, id, **kw):
        """
        Update an instance of a collection
        """
        kwargs = self.prepare_request_kwargs(kw)
        url = self.format_url("/{0}/{1}".format(self.name, id))
        return self.request("PUT", url, **kwargs)

    def delete(self, id, **kw):
        """
        Delete an instance of a collection
        """
        kwargs = self.prepare_request_kwargs(kw, json=False)
        url = self.format_url("/{0}/{1}".format(self.name, id))
        return self.request("DELETE", url, **kwargs)


class Users(CollectionClient):
    """
    Users have some special cases.
    """

    def me(self, **kw):
        """
        Fetch your user profile.
        """
        kwargs = self.prepare_request_kwargs(kw, json=False)
        url = self.format_url("/{0}/me".format(self.name))
        return self.request("GET", url, params=kwargs["params"])

    def update_me(self, **kw):
        """
        Update your user profile.
        """

        # special case for this endpoint
        kwargs = self.prepare_request_kwargs(kw, params=["refresh_apikey"])
        url = self.format_url("/{0}/me".format(self.name))
        return self.request("PUT", url, **kwargs)

    def login(self, **kw):
        """
        Login via email + password.
        """
        kwargs = self.prepare_request_kwargs(kw)
        url = self.format_url("/{0}/login".format(self.name))
        return self.request("POST", url, json=kwargs["json"])


class Files(CollectionClient):

    """
    The Files API includes additional endpoints
    for managing related collections (folder + fields)
    """

    def prepare_file_create_request_kwargs(self, kw, **kwargs):
        """
        We include a method for file creation since requests
        gets confused when you include `files` and `json`
        arguments (it defaults to setting to content-type to multipart upload,
        thereby suppressing the `json`).
        We handle this by passing `json` to the `data` argument
        and serializing the fields as a json string under
        the key 'fields'. We do serialize field_data as json
        because Flask gets confused with nested data POSTs.
        """
        kwargs = self.prepare_request_kwargs(kw, json=True)
        fields = kwargs["json"].pop("fields", {})
        folders = kwargs["json"].pop("folders", [])
        kwargs["json"].update(
            {"fields": json.dumps(fields), "folders": json.dumps(folders)}
        )
        kwargs["data"] = kwargs.pop("json")
        return kwargs

    def create(self, **kw):
        """
        """
        kwargs = self.prepare_file_create_request_kwargs(kw)
        url = self.format_url("/{0}/".format(self.name))
        return self.request("POST", url, **kwargs)

    def add_to_folder(self, id, folder_id, **kw):
        """
        Add a file to a folder.
        """
        kwargs = self.prepare_request_kwargs(kw, json=False)
        url = self.format_url("/{0}/{1}/folders/{2}".format(self.name, id, folder_id))
        return self.request("POST", url, **kwargs)

    def remove_from_folder(self, id, folder_id, **kw):
        """
        Remove a file from a folder.
        """
        kwargs = self.prepare_request_kwargs(kw, json=False)
        url = self.format_url("/{0}/{1}/folders/{2}".format(self.name, id, folder_id))
        return self.request("DELETE", url, **kwargs)

    def add_field(self, id, field_id, **kw):
        """
        Add a field to a file.
        """
        kwargs = self.prepare_request_kwargs(kw, json=True)
        url = self.format_url("/{0}/{1}/fields/{2}".format(self.name, id, field_id))
        return self.request("POST", url, **kwargs)

    def update_field(self, id, field_id, **kw):
        """
        Update a field for a file.
        """
        kwargs = self.prepare_request_kwargs(kw, json=True)
        url = self.format_url("/{0}/{1}/fields/{2}".format(self.name, id, field_id))
        return self.request("PUT", url, **kwargs)

    def remove_field(self, id, field_id, **kw):
        """
        Remove a field from a file.
        """
        kwargs = self.prepare_request_kwargs(kw, json=False)
        url = self.format_url("/{0}/{1}/fields/{2}".format(self.name, id, field_id))
        return self.request("DELETE", url, **kwargs)

    def stream(self, id, **kw):
        """
        Get the streaming file contents. Reutrns just Request for now
        """
        kwargs = self.prepare_request_kwargs(kw, json=False)
        url = self.format_url("/{0}/{1}/stream".format(self.name, id))
        return self.session.get(url, **kwargs)

    def download(self, id, **kw):
        """
        Download a file as an attachment.
        """
        kwargs = self.prepare_request_kwargs(kw, json=False)
        url = self.format_url("/{0}/{1}/download".format(self.name, id))
        return self.session.get(url, **kwargs)

    def get_store(self, **kw):
        """
        Get info about this instance's file_store.
        """
        kwargs = self.prepare_request_kwargs(kw, json=False)
        url = self.format_url("/{0}/store".format(self.name))
        return self.request("GET", url, **kwargs)


class API(BaseClient):

    """
    A class for interacting with the SickDB API.
    """

    def __init__(self, *args, **kwargs):
        BaseClient.__init__(self, *args, **kwargs)
        self.users = Users(name="users", **kwargs)
        self.folders = CollectionClient(name="folders", **kwargs)
        self.fields = CollectionClient(name="fields", **kwargs)
        self.files = Files(name="files", **kwargs)
