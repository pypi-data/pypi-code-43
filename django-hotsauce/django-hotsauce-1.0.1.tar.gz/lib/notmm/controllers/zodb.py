#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from notmm.controllers.wsgi import WSGIController
from notmm.dbapi.orm import ClientStorageProxy
logger = logging.getLogger('notmm.controllers.wsgi')

__all__ = ['ZODBController']

class ZODBController(WSGIController):

    key_prefix = 'schevo.db.'
    debug = True

    def __init__(self, request, db_name, manager=None, **kwargs):
        super(ZODBController, self).__init__(**kwargs)
        self.environ_key = self.key_prefix + 'zodb'
        self.manager = manager
        self.setup_database(db_name)
        
    def setup_database(self, db_name):
        if self.manager is None:
            #raise ValueError("Database manager is not set!")
            #Backward-compatible mode!

            self.db = ClientStorageProxy(db_name)
        else:
            try:
                #print self.manager.connections
                self.db = self.manager[db_name]
                if self.debug:
                    assert self.db is not None
            except (KeyError, AttributeError):
                raise
        if self.debug:
            logger.debug("Configured database: %s" % self.db._label)
        return None
    def init_request(self, environ):
        request = super(ZODBController, self).init_request(environ)
        if self.debug:
            assert self.environ_key == 'schevo.db.zodb' # XXX use settings.SCHEVO['DATABASE_URL']

        if not self.environ_key in request.environ:
            request.environ[self.environ_key] = self.db
        self._request = request # cheat!!!
        return request
