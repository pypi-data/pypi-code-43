from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.traces import DroppedSpan
from stackifyapm.traces import execution_context
from stackifyapm.utils.helper import is_async_span


class UrllibInstrumentation(AbstractInstrumentedModule):
    name = "urllib"

    instrument_list = [
        ("urllib", "urlopen"),
        ("urllib.request", "urlopen"),
    ]

    def call(self, module, method, wrapped, instance, args, kwargs):
        url = args[0]
        extra_data = {
            "wrapped_method": "Execute",
            "provider": self.name,
            "type": "Web External",
            "sub_type": "send",
            "url": url,
        }

        with CaptureSpan("ext.http.urllib", extra_data, leaf=True, is_async=is_async_span()) as span:
            request = wrapped(*args, **kwargs)

            if not isinstance(span, DroppedSpan):
                span.context['status_code'] = request.code
                if hasattr(request, '_method'):
                    span.context['request_method'] = request._method

                transaction = execution_context.get_transaction()
                transaction.update_span_context(span.id, span.context)

            return request
