import logging

import wrapt

from . import run_once

logger = logging.getLogger(__name__)


@run_once
def patch(tracer):
    def run_wrapper(wrapped, instance, args, kwargs):
        logger.debug("intercepting request: instance=%s args=%s kwargs=%s", instance, args, kwargs)
        with tracer.start_active_span(
                operation_name="Run %s" % instance.name):
            return wrapped(*args, **kwargs)

    def apply_async_wrapper(wrapped, instance, args, kwargs):
        logger.debug("intercepting request: instance=%s args=%s kwargs=%s", instance, args, kwargs)
        with tracer.start_active_span(
                operation_name="Apply async %s" % instance.name):
            return wrapped(*args, **kwargs)

    try:
        module = 'celery.app.task'
        name = 'Task.__call__'
        logger.debug("patching module=%s name=%s", module, name)
        wrapt.wrap_function_wrapper(module, name, run_wrapper)

        name = 'Task.apply_async'
        logger.debug("patching module=%s name=%s", module, name)
        wrapt.wrap_function_wrapper(module, name, apply_async_wrapper)
    except ImportError:
        logger.debug("module not found module=celery.app.task")
