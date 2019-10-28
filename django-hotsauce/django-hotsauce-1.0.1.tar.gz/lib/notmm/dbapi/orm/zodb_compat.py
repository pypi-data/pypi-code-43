#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from schevo.backends.zodb import ZodbBackend # require zodb 3.7.4
from ._databaseproxy import DatabaseProxy

log = logging.getLogger(__name__)

__all__ = ('ClientStorageProxy',)

class ClientStorageProxy(DatabaseProxy):
    def __init__(self, db_name, **kwargs):
        # XXX Hack.
        if not 'db_connection_cls' in kwargs:
            kwargs['db_connection_cls'] = ZodbBackend
        super(ClientStorageProxy, self).__init__(db_name, **kwargs)

