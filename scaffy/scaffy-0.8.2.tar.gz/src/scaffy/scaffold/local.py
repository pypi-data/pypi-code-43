# -*- coding: utf-8 -*-
""" Local (per user) store for scaffolds. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
from os.path import exists, join

# 3rd party imports
from cached_property import cached_property_ttl

# local imports
from scaffy.core import const
from scaffy.core import log
from .scaffold import Scaffold


class LocalStore(object):
    """ Represents the local scaffold storage.

    This is per OS user and can be used to easily manage local scaffolds.
    """
    def __init__(self, path=None):
        self.path = path or const.DEFAULT_LOCAL_STORE_PATH
        if not exists(self.path):
            os.makedirs(self.path)

    @cached_property_ttl(ttl=5)
    def scaffolds(self):
        """ List of scaffolds stored in the LocalStore.

        :return List[Scaffold]:
            A list of scaffolds in the local store.
        """
        scaffolds = []
        for filename in os.listdir(self.path):
            if filename.endswith(const.FILE_EXT):
                try:
                    path = join(self.path, filename)
                    scaffold = Scaffold.load_from_file(path)

                    scaffolds.append(scaffold)
                except Scaffold.Invalid:
                    pass

        return scaffolds

    def add(self, scaffold):
        """ Add a scaffold to the store.

        :param Scaffold scaffold:
            The scaffold that will be saved in the local store.
        """
        scaffold.write(self.path)

        self._invalidate_cache()

    def delete(self, name):
        """ Delete a scaffold from local storage.

        :param str name:
            The name of the scaffold to delete.
        """
        scaffold = self.load(name)

        if scaffold is not None:
            os.remove(scaffold.path)
            self._invalidate_cache()

        else:
            log.err("'{}' does not exist".format(name))

    def load(self, name):
        """ Load a scaffold by name.

        :param str name:
            The name of the scaffold.
        :return Optional[Scaffold]:
            If there is a scaffold under that name in the local store, a
            `Scaffold` instance representing it will be returned. Otherwise
            it will return *None*.
        """
        return next((x for x in self.scaffolds if x.name == name), None)

    def _invalidate_cache(self):
        """ Invalidate scaffold list cache.

        The cache is invalidated after 5 seconds anyway, but sometimes we want
        to force invalidation (like adding/deleting scaffolds in the store).
        """
        if 'scaffolds' in self.__dict__:
            del self.__dict__['scaffolds']
