#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2019 Jack Bortone <jack@isotopesoftware.ca>
# All rights reserved.
"""Decorator functions to interact with Schevo databases"""

from functools import wraps
from notmm.controllers.schevo import SchevoController
from notmm.controllers.zodb import ZODBController


__all__ = ('with_schevo_database', 'with_durus_database')

def with_schevo_database(dbname, controller_class=ZODBController):
    """
    Decorator that adds a Schevo database object reference
    in the ``request.environ`` dictionary.

    """
    def decorator(view_func, **kwargs):
        @wraps(view_func, **kwargs)
        def _wrapper(req, *args, **kwargs):
            wsgi_app = controller_class(req, dbname)
            req.environ[wsgi_app.environ_key] = wsgi_app.db
            response = view_func(req, **kwargs)
            return response
        return _wrapper
    return decorator

def with_durus_database(dbname, controller_class=SchevoController):
    return with_schevo_database(dbname, controller_class=controller_class)
