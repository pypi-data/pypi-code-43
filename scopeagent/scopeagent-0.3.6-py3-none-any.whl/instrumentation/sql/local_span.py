# Copyright (c) 2015 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from __future__ import absolute_import

import contextlib

import opentracing


def start_child_span(operation_name, tracer=None, parent=None, tags=None):
    """
    Start a new span as a child of parent_span. If parent_span is None,
    start a new root span.

    :param operation_name: operation name
    :param tracer: Tracer or None (defaults to opentracing.tracer)
    :param parent: parent Span or None
    :param tags: optional tags
    :return: new span
    """
    tracer = tracer or opentracing.tracer
    return tracer.start_span(
        operation_name=operation_name,
        child_of=parent.context if parent else None,
        tags=tags
    )


def func_span(func, tags=None, require_active_trace=False, tracer=None):
    """
    Creates a new local span for execution of the given `func`.
    The returned span is best used as a context manager, e.g.

    .. code-block:: python

        with func_span('my_function'):
            return my_function(...)

    At this time the func should be a string name. In the future this code
    can be enhanced to accept a real function and derive its qualified name.

    :param func: name of the function or method
    :param tags: optional tags to add to the child span
    :param require_active_trace: controls what to do when there is no active
        trace. If require_active_trace=True, then no span is created.
        If require_active_trace=False, a new trace is started.
    :return: new child span, or a dummy context manager if there is no
        active/current parent span
    """
    tracer = tracer or opentracing.tracer
    current_span = tracer.active_span

    if current_span is None and require_active_trace:
        @contextlib.contextmanager
        def empty_ctx_mgr():
            yield None

        return empty_ctx_mgr()

    # TODO convert func to a proper name: module:class.func
    operation_name = str(func)
    return start_child_span(
        operation_name=operation_name, parent=current_span, tags=tags, tracer=tracer
    )


