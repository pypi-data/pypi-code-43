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
        logger.debug("patching module=django.core.handlers.wsgi name=WSGIHandler.__call__")
        wrapt.wrap_function_wrapper('django.core.handlers.wsgi', 'WSGIHandler.__call__', wrapper)
    except ImportError:
        logger.debug("module not found module=django.core.handlers.wsgi")
