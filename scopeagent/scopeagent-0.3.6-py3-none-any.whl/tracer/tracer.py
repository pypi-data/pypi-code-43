"""
Originally derived from https://github.com/opentracing/basictracer-python.
"""
import logging
import time

import opentracing
from opentracing import Tracer as _Tracer
from opentracing import Format, UnsupportedFormatException
from opentracing.scope_managers import ThreadLocalScopeManager

from scopeagent.tracer import SpanRecorder, DefaultSampler
from scopeagent.tracer.context import SpanContext
from scopeagent.tracer.span import BasicSpan
from scopeagent.tracer.text_propagator import TextPropagator
from scopeagent.tracer.util import generate_id
from . import tags as cs_tags


logger = logging.getLogger(__name__)


class BasicTracer(_Tracer):
    def __init__(self, recorder=None, sampler=None, scope_manager=None):
        """Initialize a BasicTracer instance.
        """
        scope_manager = ThreadLocalScopeManager() \
            if scope_manager is None else scope_manager
        super(BasicTracer, self).__init__(scope_manager)

        self.recorder = NoopRecorder() if recorder is None else recorder
        self.sampler = DefaultSampler(1) if sampler is None else sampler
        self._propagators = {
            Format.TEXT_MAP: TextPropagator(),
            Format.HTTP_HEADERS: TextPropagator(),
        }

    def start_active_span(self,
                          operation_name,
                          child_of=None,
                          references=None,
                          tags=None,
                          start_time=None,
                          ignore_active_span=False,
                          finish_on_close=True):

        # create a new Span
        span = self.start_span(
            operation_name=operation_name,
            child_of=child_of,
            references=references,
            tags=tags,
            start_time=start_time,
            ignore_active_span=ignore_active_span,
        )

        return self.scope_manager.activate(span, finish_on_close)

    def start_span(self,
                   operation_name=None,
                   child_of=None,
                   references=None,
                   tags=None,
                   start_time=None,
                   ignore_active_span=False):

        start_time = time.time() if start_time is None else start_time

        # See if we have a parent_ctx in `references`
        parent_ctx = None
        if child_of is not None:
            parent_ctx = (
                child_of if isinstance(child_of, opentracing.SpanContext)
                else child_of.context)
        elif references is not None and len(references) > 0:
            # TODO only the first reference is currently used
            parent_ctx = references[0].referenced_context

        # retrieve the active SpanContext
        if not ignore_active_span and parent_ctx is None:
            scope = self.scope_manager.active
            if scope is not None:
                parent_ctx = scope.span.context

        # Assemble the child ctx
        ctx = SpanContext(span_id=generate_id())
        if parent_ctx is not None:
            if parent_ctx._baggage is not None:
                ctx._baggage = parent_ctx._baggage.copy()
            ctx.trace_id = parent_ctx.trace_id
            ctx.sampled = parent_ctx.sampled
        else:
            ctx.trace_id = generate_id()
            ctx.sampled = self.sampler.sampled(ctx.trace_id)

        # Tie it all together
        return BasicSpan(
            self,
            operation_name=operation_name,
            context=ctx,
            parent_id=(None if parent_ctx is None else parent_ctx.span_id),
            tags=tags,
            start_time=start_time)

    def inject(self, span_context, format, carrier):
        if format in self._propagators:
            self._propagators[format].inject(span_context, carrier)
        else:
            raise UnsupportedFormatException()

    def extract(self, format, carrier):
        if format in self._propagators:
            return self._propagators[format].extract(carrier)
        else:
            raise UnsupportedFormatException()

    def record(self, span):
        self.recorder.record_span(span)

    def is_test_request(self):
        return self.active_span.context.baggage.get(cs_tags.SPAN_KIND, None) == 'test'


class NoopRecorder(SpanRecorder):
    def record_span(self, span):
        pass
