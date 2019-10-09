import logging

import opentracing
import wrapt
from opentracing.ext import tags
from six.moves.urllib_parse import urlparse

from . import run_once

logger = logging.getLogger(__name__)


@run_once
def patch(tracer):
    def wrapper(wrapped, instance, args, kwargs):
        logger.debug("intercepting request: instance=%s args=%s kwargs=%s", instance, args, kwargs)
        request = args[0] if len(args) > 0 else kwargs['requests']
        parsed_url = urlparse(request.url)
        with tracer.start_active_span(
                operation_name="HTTP %s" % request.method,
                tags={
                    tags.SPAN_KIND: tags.SPAN_KIND_RPC_CLIENT,
                    tags.HTTP_URL: request.url,
                    tags.HTTP_METHOD: request.method,
                    tags.PEER_ADDRESS: parsed_url.netloc,
                    tags.PEER_PORT: parsed_url.port,
                }
        ) as scope:
            tracer.inject(scope.span.context, format=opentracing.Format.HTTP_HEADERS, carrier=request.headers)
            resp = wrapped(*args, **kwargs)
            scope.span.set_tag(tags.HTTP_STATUS_CODE, resp.status_code)
            if resp.status_code >= 400:
                scope.span.set_tag(tags.ERROR, True)
        return resp

    try:
        logger.debug("patching module=requests.adapters name=HTTPAdapter.send")
        wrapt.wrap_function_wrapper('requests.adapters', 'HTTPAdapter.send', wrapper)
    except ImportError:
        logger.debug("module not found module=requests.adapters")
