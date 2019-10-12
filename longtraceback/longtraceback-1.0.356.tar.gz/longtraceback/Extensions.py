#!/usr/bin/env python
# pylint: disable=line-too-long
"""
Additional interfaces used by the Traceback functions.

This module contains the extras supported by some forms of traceback code
in order to help diagnose issues.

__traceback_supplement__
========================
    Source of additional information for context of the operation.
    Defined in local or global scope.
    See:
        - https://web.archive.org/web/20160719224005/http://pythonpaste.org/modules/exceptions.html#module-paste.exceptions.collector
        - https://github.com/Pylons/weberror/blob/master/weberror/collector.py#L39

    Must contain a tuple, whose elements are (constructor, args...).
    The constructor function must return an object which follows the
    ITracebackSupplement protocol as defined:
        - https://docs.zope.org/zope.exceptions/api.html#itracebacksupplement

    Members:
        - warnings (optional)
            A sequence of warning messages, or None
        - column (optional)
            The column offset (0-indexed) of the exception, or None
        - source_url (optional)
            The URL of the script where the exception occurred, or None
        - line (optional)
            The line number (1-indexed) of the exception, or None
        - expression (optional)
            The expression being evaluated, or None
        - object (optional)
            Unknown, used in Paste:
                - https://bitbucket.org/ianb/paste/src/0e5a48796ab969d874c6b772c5c33561ac2d1b0d/paste/exceptions/collector.py?at=default&fileviewer=file-view-default#collector.py-245
        - getInfo() (optional)
            Returns a string containing additional information
        - extraData() (optional)
            Returns a dictionary of key-value pairs which will be accumulated into a global
            report of information about the exception.
                - https://bitbucket.org/ianb/paste/src/0e5a48796ab969d874c6b772c5c33561ac2d1b0d/paste/exceptions/collector.py?at=default&fileviewer=file-view-default#collector.py-165
                - https://github.com/Pylons/weberror/blob/master/weberror/collector.py#L167
            Used to provide more detail about the paths searched in ImportError:
                - https://bitbucket.org/ianb/paste/src/0e5a48796ab969d874c6b772c5c33561ac2d1b0d/paste/exceptions/collector.py?at=default&fileviewer=file-view-default#collector.py-369
            (Not currently supported properly)

    Status: Supported


__traceback_info__
==================
    Information to include in the traceback.
    Defined in local scope.
    See:
        - https://web.archive.org/web/20160719224005/http://pythonpaste.org/modules/exceptions.html#module-paste.exceptions.collector
        - https://github.com/Pylons/weberror/blob/master/weberror/collector.py#L39
        - https://docs.zope.org/zope.exceptions/api.html

    Contains information to include in the traceback.
    Paste defines this as a string that will be output literally.
    Zope defines this as a container whose repr will be included in the output.
    ... and yet its implementation just stringifies it:
        - https://github.com/zopefoundation/zope.exceptions/blob/master/src/zope/exceptions/exceptionformatter.py#L105

    Status: Supported


__traceback_hide__ / __tracebackhide__
======================================
    Hiding of the frame from output.
    Defined in local scope.
    See:
        - https://web.archive.org/web/20160719224005/http://pythonpaste.org/modules/exceptions.html#module-paste.exceptions.collector
        - https://github.com/pytest-dev/pytest/blob/master/_pytest/_code/code.py#L223

    Allows the stack frame, or those related to it, to be hidden from the traceback
    if they are not directly the cause of the exception.

    Values:
        - True
            The frame will be hidden.
        - 'before'
            All frames before this will be hidden
        - 'before_and_this'
            All frames before this will be hidden, and this frame too
        - 'after'
            All frames after this will be hidden (up to a 'reset' value)
        - 'after_and_this'
            All frames after this will be hidden, and this frame too (up to a 'reset' value)
        - 'reset'
            Terminates any 'after' hiding.

    Status: Supported


__traceback_reporter__
======================
    Change the reporting behaviour of the traceback
    Defined in local scope.
    "This should be a reporter object (see the reporter module), or a list/tuple
    of reporter objects. All reporters found this way will be given the exception,
    innermost first."
    See:
        - https://web.archive.org/web/20160719224005/http://pythonpaste.org/modules/exceptions.html#module-paste.exceptions.collector

    It is not clear to me that this reporting change is useful in the context
    of the longtraceback module.

    Status: NOT IMPLEMENTED


__traceback_decorator__
=======================
    Directly manipulate the collected information about the traceback frame.
    Defined in local or global scope.
    "This object (defined in a local or global scope) will get the result of
    this function (the CollectedException defined below). It may modify this
    object in place, or return an entirely new object. This gives the object
    the ability to manipulate the traceback arbitrarily.
    See:
        - https://web.archive.org/web/20160719224005/http://pythonpaste.org/modules/exceptions.html#module-paste.exceptions.collector

    It is not clear to me that this manipulation is useful in the context
    of the longtraceback module. It would require the implementation of
    Paste-like exception data collection which is not the intention of the
    existing code.

    Status: NOT IMPLEMENTED
"""


class ExtraFrameInfo(object):

    def __init__(self):
        self.frame_sections = []
        self.exception_data = {}

    def add_frame_section(self, section, style, content=None, fields=None):
        self.frame_sections.append({'section': section,
                                    'style': style,
                                    'content': content or [],
                                    'fields': fields or {}})

    def add_exception_data(self, value):
        # Normalise all the exception data to include importance.
        excdata = {}
        for title, content in value.items():
            importance = 'normal'
            if isinstance(value, tuple):
                importance = value[0]
                title = value[1]
            excdata[(importance, title)] = content

        self.exception_data.update(excdata)

    def exception_section(self):
        """
        Turn the exception data into a section to append to the frame information.
        """
        excdata = {}
        for (importance, title), content in self.exception_data.items(): # pylint: disable=unused-variable
            # Remove the 'importance' from the tuples
            excdata[title] = content

        return {'section': 'Exception Information',
                'style': 'extension.extra-info',
                'fields': excdata}

    def sections(self):
        sections = self.frame_sections[:]

        if self.exception_data:
            # Append the exception information, whilst we don't have exception-specific state
            sections.append(self.exception_section())

        return sections


def report_info(frame, extrainfo):
    """
    Report on the __traceback_info__ extension.
    """

    f_locals = frame.f_locals

    tb_info = f_locals.get('__traceback_info__', None)

    if tb_info:
        tb_info = str(tb_info)
        extrainfo.add_frame_section(section='Info',
                                    style='extension.info',
                                    content=[tb_info])


def report_supplement(frame, extrainfo):
    """
    Report on the __traceback_supplement__ extension.
    """

    f_locals = frame.f_locals
    f_globals = frame.f_globals

    tb_supplement = f_locals.get('__traceback_supplement__', None)
    if not tb_supplement:
        tb_supplement = f_globals.get('__traceback_supplement__', None)

    if not tb_supplement:
        return

    fields = {}
    func = tb_supplement[0]
    args = tb_supplement[1:]

    if callable(func):
        obj = func(*args)

        for field in ('warnings', 'column', 'line', 'source_url', 'expression', 'object'):
            value = getattr(obj, field, None)
            if value is not None:
                field = field.replace('_', ' ')
                fields[field] = value

        for funcname, field in (('getInfo', 'info'),
                                ('extraData', 'exception data')):
            func = getattr(obj, funcname, None)
            if func is not None:
                value = func()
                if field == 'info':
                    fields[field] = value
                else:
                    # The exception data is actually a separate block
                    # from the Supplement, because it is intended to
                    # relate to the exception, rather than to this
                    # specific frame.
                    if isinstance(value, dict):
                        extrainfo.add_exception_data(value)

        if fields:
            extrainfo.add_frame_section(section='Supplement',
                                        style='extension.supplement',
                                        fields=fields)

    else:
        extrainfo.add_frame_section(section='Supplement',
                                    style='extension.supplement',
                                    fields={'bad-tuple': tb_supplement})

def frame_extensions(frame):
    """
    Report on any frame extensions that have been set.

    @param frame:   The stack frame to report extensions info from

    @return:    a list of sections to report, each a dictionary:
                    'section'   Name of the section
                    'syle'      Style to apply to the section header and content
                    'content'   A list of strings to present (optional)
                    'fields'    A dictionary of field-value pairs (optional)
    """

    extrainfo = ExtraFrameInfo()

    report_info(frame, extrainfo)
    report_supplement(frame, extrainfo)

    return extrainfo.sections()


def frames_filter(frames):
    """
    Filter any frames out which are not interesting according to the pytest/paste rules.

    The variables we look for are '__traceback_hide__' or '__tracebackhide__' defined in local scope.

    Allows the stack frame, or those related to it, to be hidden from the traceback
    if they are not directly the cause of the exception.

    Values:
        - True
            The frame will be hidden.
        - 'before'
            All frames before this will be hidden
        - 'before_and_this'
            All frames before this will be hidden, and this frame too
        - 'after'
            All frames after this will be hidden (up to a 'reset' value)
        - 'after_and_this'
            All frames after this will be hidden, and this frame too (up to a 'reset' value)
        - 'reset'
            Terminates any 'after' hiding.
    """

    new_frames_list = []
    ignore_subsequent_frames = False
    if len(frames) == 0:
        return frames

    last_frame = frames[-1]
    for frame in frames:
        tb_frame = getattr(frame, 'tb_frame', None)
        f_locals = getattr(tb_frame, 'f_locals', {})

        # Two known forms for the hide variable.
        hide = f_locals.get('__traceback_hide__', None)
        if hide is None:
            hide = f_locals.get('__tracebackhide__', None)

        if hide is not None:
            if hide == 'reset':
                ignore_subsequent_frames = False
            elif hide == 'after':
                ignore_subsequent_frames = True
                # But keep this frame:
                if frame != last_frame:
                    new_frames_list.append(frame)
            elif hide == 'after_and_this':
                ignore_subsequent_frames = True
            elif hide == 'before':
                if frame != last_frame:
                    new_frames_list = []
            elif hide == 'before_and_this':
                if frame != last_frame:
                    new_frames_list = []
                    continue
            elif hide == True:
                # This frame is hidden
                if frame != last_frame:
                    continue

        if not ignore_subsequent_frames:
            new_frames_list.append(frame)

    if not new_frames_list:
        # If everything would have been hidden, always keep the last frame.
        new_frames_list = [last_frame]

    return new_frames_list
