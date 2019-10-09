#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import opentracing
import requests
from cdumay_opentracing import Span
from cdumay_http_client.client import HttpClient


class RequestSpan(Span):
    FORMAT = opentracing.Format.HTTP_HEADERS
    TAGS = ['url', 'method']

    @classmethod
    def name(cls, obj):
        return "{method} {url}".format_map(obj)

    @classmethod
    def extract(cls, obj):
        """ Extract span context from the given object

        :param Any obj: Object to use as context
        :return: a SpanContext instance extracted from the inner span object or None if no
            such span context could be found.
        """
        return opentracing.tracer.extract(cls.FORMAT, obj['headers'])

    @classmethod
    def inject(cls, span, obj):
        """ Injects the span context into a `carrier` object.

        :param opentracing.span.SpanContext span: the SpanContext instance
        :param Any obj: Object to use as context
        """
        opentracing.tracer.inject(span, cls.FORMAT, obj['headers'])

    @classmethod
    def _postrun(cls, span, obj, **kwargs):
        """ Trigger to execute just before closing the span

        :param opentracing.span.Span  span: the SpanContext instance
        :param Any obj: Object to use as context
        :param dict kwargs: additional data
        """
        span.set_tag("response.status_code", obj.status_code)
        span.set_tag(
            "response.content_lenght", len(getattr(obj, 'content', ""))
        )

    @classmethod
    def extract_tags(cls, obj):
        """ Extract tags from the given object

        :param Any obj: Object to use as context
        :return: Tags to add on span
        :rtype: dict
        """
        return dict(
            [("request.{}".format(attr), obj.get(attr, None)) for attr in
             cls.TAGS]
        )


class OpentracingHttpClient(HttpClient):
    def _request_wrapper(self, **kwargs):
        with opentracing.tracer.start_span(
                obj=kwargs, span_factory=RequestSpan) as span:
            RequestSpan.inject(span, kwargs)
            span.obj = requests.request(**kwargs)
            return span.obj
