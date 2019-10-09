import logging

import wrapt

from . import run_once
from .wrappers.wsgi import wrap_wsgi

logger = logging.getLogger(__name__)


@run_once
def patch(tracer):
    def wrapper(wrapped, instance, args, kwargs):
        return wrap_wsgi(wrapped, tracer)(*args, **kwargs)

    try:
        logger.debug("patching module=flask.app name=Flask.__call__")
        wrapt.wrap_function_wrapper('flask.app', 'Flask.__call__', wrapper)
    except ImportError:
        logger.debug("module not found module=flask.app")
