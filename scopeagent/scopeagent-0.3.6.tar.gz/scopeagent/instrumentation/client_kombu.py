import logging

import opentracing
import wrapt

from . import run_once
from ..tracer import tags

logger = logging.getLogger(__name__)


@run_once
def patch(tracer):
    def publish_wrapper(wrapped, instance, args, kwargs):
        logger.debug("intercepting request: instance=%s args=%s kwargs=%s", instance, args, kwargs)
        headers = kwargs.get('headers', {})
        with tracer.start_active_span(
                operation_name="Publish message",
                tags={
                    tags.SPAN_KIND: tags.SPAN_KIND_PUBLISH,
                }) as scope:
            tracer.inject(scope.span.context, format=opentracing.Format.HTTP_HEADERS, carrier=headers)
            kwargs['headers'] = headers
            return wrapped(*args, **kwargs)

    def receive_wrapper(wrapped, instance, args, kwargs):
        logger.debug("intercepting request: instance=%s args=%s kwargs=%s", instance, args, kwargs)
        message = args[0] if len(args) >= 1 else kwargs.get('message')
        headers = message.headers
        try:
            context = tracer.extract(format=opentracing.Format.HTTP_HEADERS, carrier=headers)
        except opentracing.SpanContextCorruptedException:
            context = None

        with tracer.start_active_span(
                child_of=context,
                operation_name="Receive message",
                tags={
                    tags.SPAN_KIND: tags.SPAN_KIND_RECEIVE,
                }):
            return wrapped(*args, **kwargs)

    try:
        logger.debug("patching module=kombu.messaging name=Producer.publish")
        wrapt.wrap_function_wrapper('kombu.messaging', 'Producer.publish', publish_wrapper)
        logger.debug("patching module=kombu.messaging name=Consumer._receive_callback")
        wrapt.wrap_function_wrapper('kombu.messaging', 'Consumer._receive_callback', receive_wrapper)
    except ImportError:
        logger.debug("module not found module=kombu.messaging")
