# -*- coding: utf-8 -*-
""" Scaffold API client. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import tempfile

# 3rd party imports
import attr

# local imports
from . import ApiError, ApiClientSectionBase
from . import util


class ScaffoldApi(ApiClientSectionBase):
    """ Handle interaction with scaffold API.

    This should never  be created and only accessed through `Client` instance as
    `Client().scaffold`.
    """
    def list(self):
        """ Return a list of all scaffolds stored in the hub by the user.

        :return List[RemoteScaffold]:
            List of scaffolds stored on scaffyhub.
        """
        r = self.api.get('/api/scaffold')
        if r.status_code != 200:
            raise ApiError(r, "Failed to get list of scaffolds: {}".format(
                r.json()['detail']
            ))

        return [RemoteScaffold.from_dict(self.api, x) for x in r.json()]

    def get_by_name(self, name):
        """ Get scaffold metadata by name.

        :param str name:
            The name of the scaffold.
        :return RemoteScaffold:
            The remote scaffold metadata. You can download the actual scaffold
            file using `RemoteScaffold.download()`
        """
        for item in self.list():
            if item.name == name:
                return item

        return None

    def upload(self, scaffold):
        """ Upload the scaffold to scaffyhub.

        :param scaffy.scaffold.Scaffold scaffold:
            The scaffold to upload
        :return RemoteScaffold):
            A `RemoteScaffold` instance that represents the uploaded scaffold.
        """
        if scaffold.path is None:
            raise NotImplementedError(
                "No support for scaffolds not loaded from a file"
            )

        with open(scaffold.path, 'rb') as fp:
            r = self.api.post('/api/scaffold', files={'file': fp})

        if r.status_code != 201:
            raise ApiError(r, "Failed to push {}".format(scaffold.name))

        return RemoteScaffold.from_dict(self.api, r.json())


@attr.s
class RemoteScaffold(object):
    """ Represents a scaffold stored on scaffyhub.

    You should never need to create instances of this class manually and
    only receive them as results of scaffold API calls.
    """
    api = attr.ib()

    id = attr.ib(default=None)
    name = attr.ib(default=None)
    created = attr.ib(default=None, convert=util.parse_date)
    size = attr.ib(default=None)
    config = attr.ib(default=None)
    owner_id = attr.ib(default=None)
    sha1 = attr.ib(default=None)
    filename = attr.ib(default=None)

    @classmethod
    def from_dict(cls, client, values):
        """ Create new instance from a dictionary of values.

        :param scaffy.remote.Client client:
            API client instance. This is used to issue all API calls related
            to this instance (like download).
        :param dict values:
            A dict of values to use for the new instance. This is most likely
            returned by an API call.
        :return RemoteScaffold:
            A `RemoteScaffold` instance initialized with the given *values*.
        """
        values['api'] = client
        return RemoteScaffold(**values)

    def download(self, out_path=None, buff_size=16 * 1024):
        """

        :param str out_path:
            Path where the file will be saved. If not given, the scaffold will
            be downloaded into a temporary file.
        :param int buff_size:
            Read buffer size. This is the size of the buffer used to read the
            scaffyhub response.
        :return str:
            Path to the downloaded scaffold file. If no *out_path* was given,
            then this will be a path to a temporary file. The caller is
            responsible for deleting it (or leaving it to the OS).
        """
        r = self.api.get(
            '/api/scaffold/{}/download'.format(self.id),
            stream=True
        )

        if r.status_code != 200:
            raise ApiError(r, "Failed to download {}".format(self.name))

        if out_path is not None:
            fp = open(out_path, 'wb')
        else:
            fd, out_path = tempfile.mkstemp()
            fp = os.fdopen(fd, 'wb')

        for chunk in r.iter_content(chunk_size=buff_size):
            fp.write(chunk)

        fp.close()

        return out_path

    def delete(self):
        """
        Delete ScaffyHub item represented by this instance.

        :raises ApiError:
            Raised when there is any problem with the API call, including an
            unexpected status code.
        """
        r = self.api.delete('/api/scaffold/{}'.format(self.id))

        if r.status_code != 204:
            raise ApiError(r, "Failed to delete {}".format(self.name))
