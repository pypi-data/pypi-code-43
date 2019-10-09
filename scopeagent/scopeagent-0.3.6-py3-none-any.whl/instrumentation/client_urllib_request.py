"""
Wraps urllib.request (f.k.a. urllib2).
"""
import logging

import opentracing
import six
import wrapt
from opentracing.ext import tags
from six.moves.urllib_parse import urlparse

from . import run_once

logger = logging.getLogger(__name__)


@run_once
def patch(tracer):
    def wrapper(wrapped, instance, args, kwargs):
        logger.debug("intercepting request: instance=%s args=%s kwargs=%s", instance, args, kwargs)

        request = args[1] if len(args) > 1 else kwargs['req']
        # Is there any better way to get this?
        if hasattr(request, 'full_url'):
            url = request.full_url  # py3
        else:
            url = request._Request__original  # py2
        parsed_url = urlparse(url)
        method = request.get_method()
        with tracer.start_active_span(
                operation_name="HTTP %s" % method,
                tags={
                    tags.SPAN_KIND: tags.SPAN_KIND_RPC_CLIENT,
                    tags.HTTP_URL: url,
                    tags.HTTP_METHOD: method,
                    tags.PEER_ADDRESS: parsed_url.netloc,
                    tags.PEER_PORT: parsed_url.port,
                }
        ) as scope:
            tracer.inject(scope.span.context, format=opentracing.Format.HTTP_HEADERS, carrier=request.headers)
            resp = wrapped(*args, **kwargs)
            scope.span.set_tag(tags.HTTP_STATUS_CODE, resp.code)
            if resp.code >= 400:
                scope.span.set_tag(tags.ERROR, True)
        return resp

    if six.PY2:
        module = 'urllib2'
    else:
        module = 'urllib.request'
    name = 'AbstractHTTPHandler.do_open'
    logger.debug("patching module=%s name=%s", module, name)
    try:
        wrapt.wrap_function_wrapper(module, name, wrapper)
    except ImportError:
        logger.debug("module not found module=%s", module)
