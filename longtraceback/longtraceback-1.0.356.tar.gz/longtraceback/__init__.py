#!/usr/bin/env python
# coding: utf-8
"""
Alternative traceback to give more information about problems.

See README.md for features.
"""

from __future__ import print_function

import inspect
import itertools
import linecache
import os
import re
import sys
import traceback
import types
import collections

from longtraceback.ReduceFilename import presentation_filename
import longtraceback.CodeNaming
import longtraceback.DescribeSequence
#import longtraceback.ValueFormat as ValueFormat
import longtraceback.Styling
import longtraceback.Extensions
import longtraceback.Options
import longtraceback.Variables
import longtraceback.ChangedVariables


# Constructor for the StyledString
StyledString = longtraceback.Styling.StyledString

# Remember the old traceback code so that we can call the functions directly.
sys_excepthook = sys.excepthook
traceback_extract_stack = traceback.extract_stack
traceback_extract_tb = traceback.extract_tb
traceback_format_list = traceback.format_list
traceback_format_exception = traceback.format_exception
traceback_print_exception = traceback.print_exception
traceback_print_tb = traceback.print_tb
traceback_print_list = traceback.print_list
traceback_format_exception_only = traceback.format_exception_only
traceback_format_final_exc_line = traceback._format_final_exc_line  # pylint: disable=protected-access


# Allow us to capture using cStringIO if we have it, or the pure python StringIO.
# May allow us to function on non-CPython systems.
IOClass = None
try:
    import cStringIO
    IOClass = cStringIO
except ImportError:
    import io
    IOClass = io


# Ensure that we can check basestring and unicode on Python 2 and 3.
try:
    basestring
except NameError:
    basestring = str  # pylint: disable=redefined-builtin

try:
    unicode
except NameError:
    unicode = str  # pylint: disable=redefined-builtin


# A FrameSummary is returned as part of the extract_tb, extract_stack interface.
# In python 2.x, this was a tuple of these entries, but under Python 3.x this is a
# class containing a number of named elements. We structure our returns as a
# namedtuple, as this allows us to meet both requirements. In the future this may
# change to a class, in line with Python 3's usage,.
FrameSummary = collections.namedtuple('FrameSummary', ('filename', 'lineno', 'name', 'line'))
# Locals are not returned as part of the tuple (to match Python 2 usage), but are
# available by name (but at present will be None).
FrameSummary.locals = None


def apply_styling(func):
    """
    Decorator to apply styling to any strings returned
    """
    def applied_styling(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, list):
            return [str(part) for part in result]

        if not isinstance(result, basestring):
            return str(result)

        return result

    return applied_styling


class EvaluationFailure(object):
    """
    Base class for errors within the values.
    """
    def __init__(self, msg=None):
        self._msg = msg

    def __repr__(self):
        if self._msg:
            return "<error evaluating value: %s>" % (self._msg,)

        return "<error evaluating value>"


class InvalidAttribute(EvaluationFailure):

    def __init__(self, on_object, name, msg=None):
        super(InvalidAttribute, self).__init__(msg)
        self._on = on_object.__class__.__name__
        self._name = name

    def __repr__(self):
        if self._msg:
            return "<invalid attribute '%s' on %s object: %s>" % (self._name, self._on, self._msg)

        return "<invalid attribute '%s' on %s object>" % (self._name, self._on)


class InvalidParameter(EvaluationFailure):

    def __init__(self, name, msg=None):
        super(InvalidParameter, self).__init__(msg)
        self._name = name

    def __repr__(self):
        if self._msg:
            return "<undefined parameter '%s': %s>" % (self._name, self._msg)

        return "<undefined parameter '%s'>" % (self._name)


def flatten_sequence(*args):
    """
    Flatten any sequence of sequences into a single sequence of values.
    """
    for l in args:
        for el in l:
            if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
                for sub in flatten_sequence(el):
                    yield sub
            else:
                yield el


def _join_list(line_list, between='', add_newline=True):
    """
    Join all the elements of a list into a string.

    The 'join' method will not work with non-string elements.
    The 'sum' function is explicitly prevented from working on
    string elements.
    """
    if all((isinstance(line, basestring) for line in line_list)):
        # this is a simple string
        if add_newline:
            return between.join(line + '\n' for line in line_list)
        else:
            return between.join(line_list)

    if between == '' and \
       all((isinstance(line, (longtraceback.Styling.StyledStringClass, basestring)) for line in line_list)):
        # this is only StyledStrings or basestrings
        if add_newline:
            return sum((line + '\n' for line in line_list), StyledString(''))
        else:
            return sum(line_list, StyledString(''))

    # There are a mixture of other object in the list, so we manually accumulate them
    lines = ''
    first = True
    for line in line_list:
        if not first and between:
            lines += between
        first = False
        if add_newline:
            lines += line + '\n'
        else:
            lines += line

    return lines


# Replacement 'inspect.formatargvalues' which uses _join_list instead of string.join.
# This allows us to use StyledStrings instead of regular strings within the values
# returned.
def _formatargvalues(args, varargs, varkw, varsdict,
                     formatarg=str,
                     formatvarargs=lambda name: '*' + name,
                     formatvarkw=lambda name: '**' + name,
                     formatvalue=lambda value: '=' + repr(value)):
    """Format an argument spec from the 4 values returned by getargvalues.

    The first four arguments are (args, varargs, varkw, locals).  The
    next four arguments are the corresponding optional formatting functions
    that are called to turn names and values into strings.  The ninth
    argument is an optional function to format the sequence of arguments."""
    def convert(name, varsdict=varsdict,
                formatarg=formatarg, formatvalue=formatvalue):
        return formatarg(name) + formatvalue(varsdict.get(name, InvalidParameter(name)))
    specs = []
    for arg in args:
        if isinstance(arg, list):
            # Python 2 style tuples passed to functions
            specs.append(_formatargvalues(arg, None, None, varsdict,
                                          formatarg=formatarg,
                                          formatvarargs=formatvarargs,
                                          formatvarkw=formatvarkw,
                                          formatvalue=formatvalue))
        else:
            specs.append(convert(arg))
    if varargs:
        specs.append(formatvarargs(varargs) + formatvalue(varsdict[varargs]))
    if varkw:
        specs.append(formatvarkw(varkw) + formatvalue(varsdict[varkw]))
    return '(' + _join_list(specs, ', ', add_newline=False) + ')'


# Our options for the traceback
options = longtraceback.Options.LongTracebackOptions()
try:
    options.read_user_config_file()
except Exception:  # pylint: disable=broad-except
    # FIXME: Report the failure?
    options = longtraceback.Options.LongTracebackOptions()


class TrapExceptions(object):
    """
    Trap all exceptions within this context, recording them for later.

    This context handler is intended to be used to retain the exceptions for later reporting,
    so that we can report the internal exceptions alongside each of the frames which triggered
    them. Without the context handlers, the exceptions will just be reported at the time of
    their discovery, resulting in their failures being reported before any actual printing of
    the exception messages.
    """
    current_traceback_frame = None

    def __init__(self, name, frame=None, usage='Internal exception'):
        self.name = name
        self.frame = frame
        self.usage = usage
        self.prior_frame = None
        self.in_use = False

    def __enter__(self):
        if self.in_use:
            raise RuntimeError('Attempt to enter TrapExceptions twice')
        self.in_use = True
        self.prior_frame = TrapExceptions.current_traceback_frame
        TrapExceptions.current_traceback_frame = self.frame

    def __exit__(self, exctype, exc, tb):
        if not self.in_use:
            raise RuntimeError('Attempt to exit TrapExceptions twice, or before entered')
        if exc:
            internal_exception(self.name, exc, tb=tb)
        TrapExceptions.current_traceback_frame = self.prior_frame
        self.prior_frame = None
        self.in_use = False


def internal_exception(name, ex, tb=None, usage='Internal exception'):
    if not options.internal_traceback:
        return

    text = format_internal_exception(name, ex, tb, usage=usage)

    # Ensure that every line is in the internal-exception context
    text = [StyledString(line, style='internal-exception') for line in text]

    if TrapExceptions.current_traceback_frame:
        TrapExceptions.current_traceback_frame.exceptions.append(text)
    else:
        for line in text:
            print(line)


def format_internal_exception(name, ex, tb=None, indent=0, usage='Internal exception'):
    text = []

    indent_str = ' ' * indent

    text.append(indent_str +
                StyledString("{} [{}]:", style='header').format(usage,
                                                                StyledString(name, style='processing')))
    line = StyledString(ex.__class__.__name__, style='exception-name') + ": " + \
           StyledString(str(ex), 'exception-message')
    text.append(indent_str + "  " + line)
    if tb is None:
        # Python 3: Exceptions have a __traceback__ attribute which we can use
        tb = getattr(ex, '__traceback__', None)
        if tb is None:
            # Python 2: Fall back to the last generated exception's traceback.
            tb = sys.exc_info()[2]
    try:
        last = None
        last_repetitions = 0
        for line in traceback_format_list(traceback_extract_tb(tb)):
            if line == last:
                last_repetitions += 1
                continue
            elif last_repetitions > 0:
                text.append(indent_str + "  " + options.frame_repetition_message.format(last_repetitions))
                last_repetitions = 0
            last = line
            for subline in line.splitlines():
                text.append(indent_str + subline)
        if last_repetitions > 0:
            text.append(indent_str + "  " + options.frame_repetition_message.format(last_repetitions))

    except Exception as intex:    ## pylint: disable=broad-except
        text.append(StyledString("  Internal exception printing exception [{}]:",
                                 style='header').format(StyledString(name, style='processing')))
        line = StyledString(intex.__class__.__name__, style='exception-name') + ": " + \
               StyledString(str(intex), 'exception-message')
        text.append(indent_str + "    " + line)
        tb = sys.exc_info()[2]
        last = None
        last_repetitions = 0
        for line in traceback_format_list(traceback_extract_tb(tb)):
            if line == last:
                last_repetitions += 1
                continue
            elif last_repetitions > 0:
                text.append(indent_str + "  " + options.frame_repetition_message.format(last_repetitions))
                last_repetitions = 0
            last = line
            for subline in line.splitlines():
                text.append(indent_str + "  " + subline)
        if last_repetitions > 0:
            text.append(indent_str + "  " + options.frame_repetition_message.format(last_repetitions))

    text.append("")

    return text


class make_repr_safe(object):
    """
    Make a 'safe' repr operation, so that we do not fail to report problems in
    representing objects.
    """

    # a cache of the ids of the failed reprs, so that we do not report the
    # exceptions multiple times
    cached_repr_failures = {}

    def __init__(self):
        self.old_repr = None
        self.builtins = globals()['__builtins__']
        if isinstance(self.builtins, types.ModuleType):
            self.builtins = self.builtins.__dict__
        if options.experimental_repr:
            import longtraceback.ReprPatching  # pylint: disable=redefined-outer-name
            self.patch = longtraceback.ReprPatching
        else:
            self.patch = None

    def __enter__(self):
        if self.patch:
            self.patch.enable_patch()
        def safe_repr(obj):
            try:
                result = self.old_repr(obj)
                return result
            except Exception as exc:  # pylint: disable=broad-except
                # A failure inside the repr function means we need to make the
                # object rendering outselves
                obj_id = id(obj)
                excstr = str(exc)
                obj_name = obj.__class__.__name__
                excvalue = excstr

                # We report different messages for different places we exceed the limit.
                # For simplicity, we only show one of those per object.
                if isinstance(exc, RuntimeError) and \
                   excvalue.lower().startswith('maximum recursion depth'):
                    excvalue = 'maximum recursion depth exceeded'

                if self.cached_repr_failures.get(obj_id, None) != excvalue:
                    internal_exception('getting repr of %s' % (obj_name,),
                                       exc, usage='Exception during traceback')
                    self.cached_repr_failures[obj_id] = excvalue
                return "<object '%s', __repr__ error: '%s'>" % (obj_name,
                                                                excstr)

        self.old_repr = self.builtins['repr']
        self.builtins['repr'] = safe_repr

        return self

    def __exit__(self, exctype, exc, tb):
        self.builtins['repr'] = self.old_repr
        if self.patch:
            self.patch.disable_patch()


class SparseList(list):
    """
    Simple implementation of a sparse list.

    Isn't really sparse; pads its entries by adding None padding.

    We don't handle negative indices well - the index referenced will change depending on what
    entries have been set, because we reference the highest entry in the list.
    """

    def __setitem__(self, index, value):
        if index < 0:
            index = len(self) + index
            if index < 0:
                return

        missing = index - len(self) + 1
        if missing > 0:
            self.extend([None] * missing)
        list.__setitem__(self, index, value)

    def __getitem__(self, index):
        # Note: We don't handle slices that cross bounds
        try:
            return list.__getitem__(self, index)
        except IndexError:
            return None


def resolve_scope(module_name, code):
    """
    Resolve the scope name for a code object provided its module name.

    @return: Name of the function, as qualified as possible.
             Type of function ('UNKNOWN', 'FUNC', 'METHOD', 'GETTER', 'SETTER', 'DELETER', 'INNERFUNC', 'MODULE')
    """
    code_elements = longtraceback.CodeNaming.CodeElements(module_name)
    return code_elements.resolve(code)


class NotCalculated(object):
    """
    A marker to indicate that we have not yet calculated a value.
    """
    pass


def cachedproperty(func):
    """
    Decorate a property value to be cached.

    Object property which will only be called once, and the result cached for subsequent calls.
    The cache is held on the object for which the cache exists, so will only have the lifetime of
    the object on which it is a property.
    """
    varname = "_" + func.__name__
    @property
    def cache(self, varname=varname):
        value = getattr(self, varname, NotCalculated)
        if value is NotCalculated:
            value = func(self)
            setattr(self, varname, value)
        return value

    @cache.setter
    def cache(self, value, varname=varname):
        setattr(self, varname, value)

    @cache.deleter
    def cache(self, varname=varname):
        setattr(self, varname, NotCalculated)

    return cache


class FunctionFrame(object):
    """
    Representation of a function name, within the traceback extracted values.

    The representation provides information about the function and the variables
    which are present in the frame.

    When used as a string, returns the function name, together with some
    prototypes.

    @ivar frame:        The frame we represent
    @ivar module_name:  The name of this module, possibly extracted from filename
    @ivar full_name:    The full name, with resolved scope within the modules, classes and function
    @ivar type:         Capitalised type of the function (from resolve_scope)
    @ivar f_args:       Function arguments (from inspect.getargvalues)
    @ivar f_varargs:    Function variable argument variable name (from inspect.getargvalues)
    @ivar f_kwargs:     Function keyword argument variable (from inspect.getargvalues)
    @ivar f_locals:     Function locals (from inspect.getargvalues)
    @ivar params:       Parameters string as they might be declared
    @ivar params_styled:        Parameters string as they might be declared (but using styling)
    @ivar param_declaration:    List of parameter declarations
    @ivar param_name:           List of parameter names (with the * and ** prepended)
    @ivar changed_variables:    List of variables that may have been changed since function start
    @ivar locals:       Variables, with modules removed
    @ivar extensions:   Any extensions fields (see Extensions.py, frame_extensions)
    """

    def __init__(self, frame):
        """
        Create a new object to describe the function within the frame.

        @param frame:   The frame to extract information from
        """
        self.frame = frame

        self.exceptions = []

        global_vars = frame.f_globals

        # For the faked frames created by Jinja2, there may not be any valid __name__.
        self.module_name = global_vars.get('__name__', None)

        if not self.module_name:
            # Module is not named, but we may be able to get a filename from the
            # code object and name it through that.
            filename = frame.f_code.co_filename
            _, leafname = os.path.split(filename)
            if leafname.endswith('.py'):
                self.module_name = leafname[:-3]
        self.full_name, self.type = resolve_scope(self.module_name, frame.f_code)

        self.f_args, self.f_varargs, self.f_kwargs, self.f_locals = inspect.getargvalues(frame)

        self.param_declaration = self.f_args[:]
        self.param_names = self.f_args[:]
        if self.f_varargs:
            self.param_names.append(self.f_varargs)
            self.param_declaration.append('*' + self.f_varargs)
        if self.f_kwargs:
            self.param_names.append(self.f_kwargs)
            self.param_declaration.append('**' + self.f_kwargs)

        localvars = frame.f_locals
        # We exclude the module items (in case at local scope they import'd
        # more modules, which wouldn't be as useful to us)
        locals_without_modules = dict(obj for obj in list(localvars.items())
                                      if not isinstance(obj[1], types.ModuleType))

        self.locals = locals_without_modules

    # pylint: disable=method-hidden
    @cachedproperty
    def params_styled(self):
        """
        Styled string parameters, including the surrounding brackets.
        """
        try:
            def style_arg(name):
                return StyledString(name, style='varname')
            def style_varargs(name):
                return StyledString('*' + name, style='varname')
            def style_kwargs(name):
                return StyledString('**' + name, style='varname')
            def style_value(value):
                value_string = repr(value)
                # The value looks odd when multiline strings are formatted like this:
                #value_string = format_variable(value, None, 0)
                return '=' + StyledString(value_string, style='varvalue')

            with make_repr_safe():
                return _formatargvalues(self.f_args,
                                        self.f_varargs, self.f_kwargs,
                                        self.f_locals,
                                        formatarg=style_arg,
                                        formatvarargs=style_varargs,
                                        formatvarkw=style_kwargs,
                                        formatvalue=style_value)
        except Exception as ex:  # pylint: disable=W0703
            internal_exception("Formatting styled parameters for function %s" % (self.full_name,), ex)
            return '(<unknown>)'

    @cachedproperty
    def params(self):
        """
        Simple string parameters, including the surrounding brackets.
        """
        try:
            with make_repr_safe():
                return inspect.formatargvalues(self.f_args, self.f_varargs, self.f_kwargs,
                                               self.f_locals)
        except Exception as ex:  # pylint: disable=W0703
            internal_exception("Formatting parameters for function %s" % (self.full_name,), ex)
            return '(<unknown>)'

    @cachedproperty
    def extensions(self):
        """
        Parsing of the extensions to give additional fields.

        Only reported when we need to - which will usually be all the time, but
        can be skipped if we fall back to old style traceback.
        """

        # We do not calculate the extensions until we need to - in the case where
        # the caller does not invoke our backtrace code, it saves a little work
        # and makes the call safer.
        return longtraceback.Extensions.frame_extensions(self.frame)

    @cachedproperty
    def changed_variables(self):
        # It's possible that since the start of the function, those values were modified.
        # To check whether they have, we're going to use the incredibly rudimentary check
        # of the source lines between the start of the function and the current location.
        try:
            return longtraceback.ChangedVariables.changed_vars(self.frame)
        except Exception:  # pylint: disable=W0703
            # If anything goes wrong working out the variables, just give up.
            return None

    def clear(self):
        """
        Clear the context of the FunctionFrame.

        Ensure that all the variables are cleared so that we do not hold any
        recursive references.
        """
        self.module_name = str(self.module_name)
        self.full_name = str(self.full_name)
        self.param_names = []
        self.locals.clear()
        self.f_args = None
        self.f_varargs = None
        self.f_kwargs = None
        self.f_locals = None

        # Setters to clear cached values.
        self.params = None
        self.params_styled = None
        self.changed_variables = None
        self.extensions = None

    def params_as_variables(self, expand_args=False):
        """
        Return the parameters to this function as a dictionary of values and an order.

        @param expand_args:     Whether we should expand the varargs and kwargs parameters
                                into separate variables.
        """
        variables = {}
        order = []
        if self.f_args:
            # We must flatten the sequence so that the parameters that are assigned in tuples
            # are handled in a linear way.

            for var in flatten_sequence(self.f_args):
                try:
                    variables[var] = self.f_locals[var]
                except Exception as exc:  # pylint: disable=broad-except
                    variables[var] = EvaluationFailure(repr(exc))
                order.append(var)

        if self.f_varargs:
            if expand_args:
                for position, arg in enumerate(self.f_locals[self.f_varargs]):
                    name = '*%s[%d]' % (self.f_varargs, position)
                    try:
                        variables[name] = arg
                    except Exception as exc:  # pylint: disable=broad-except
                        variables[name] = EvaluationFailure(repr(exc))
                    order.append(name)
            else:
                name = '*%s' % (self.f_varargs,)
                try:
                    variables[name] = self.f_locals[self.f_varargs]
                except Exception as exc:  # pylint: disable=broad-except
                    variables[name] = EvaluationFailure(repr(exc))
                order.append(name)

        if self.f_kwargs:
            if expand_args:
                for key, value in self.f_locals[self.f_kwargs].items():
                    name = '**%s[%s]' % (self.f_kwargs, key)
                    try:
                        variables[name] = value
                    except Exception as exc:  # pylint: disable=broad-except
                        variables[name] = EvaluationFailure(repr(exc))
                    order.append(name)
            else:
                name = '**%s' % (self.f_kwargs,)
                try:
                    variables[name] = self.f_locals[self.f_kwargs]
                except Exception as exc:  # pylint: disable=broad-except
                    variables[name] = EvaluationFailure(repr(exc))
                order.append(name)

        return variables, order

    def __str__(self):
        """
        Return a string representation of the function, together with the parameters
        if so configured.
        """
        funcname = self.full_name
        if self.params:
            funcname += self.params

        if options.show_changed_variables:
            if self.changed_variables is None:
                # Indicates that we got an error whilst working out what's changed.
                funcname += "  [parameters may have been modified]"
            else:
                try:
                    changed_params = [name for name in flatten_sequence(self.param_names)
                                      if name in self.changed_variables]

                    if changed_params:
                        funcname += "  [%s may have been modified]" % (_join_list(changed_params, between=', '),)
                except Exception as ex:  # pylint: disable=broad-except
                    internal_exception("Formatting function %s" % (self.full_name,), ex)

        return funcname


class LineFrame(object):
    """
    The LineFrame object represents the details about line and context.

    When used as a string, returns just the trailing line (the one in the frame).
    Can be iterated to read the lines in the file (or None where the line is not
    cached).
    """
    def __init__(self, tb_or_frame):
        """
        Construct a LineFrame using either a traceback object or a stack frame.
        """
        if inspect.isframe(tb_or_frame):
            frame = tb_or_frame
            tb = None
            lineno = frame.f_lineno
        else:
            tb = tb_or_frame
            frame = tb.tb_frame
            lineno = tb.tb_lineno

        code = frame.f_code
        filename = code.co_filename

        self.lineno = lineno
        self.lines = SparseList()

        # Get the bounds from the code block itself.
        lowline, highline = longtraceback.CodeNaming.code_line_bounds(code)

        # Range of source lines to report, limited by the line definition
        linecache.checkcache(filename)
        if lowline is None or highline is None:
            # We do not understand the bounds of this code block, so we'll try to
            # display around it.
            lowline = lineno - options.line_context
            highline = lineno
        else:
            lowline = max(lineno - options.line_context, lowline)
            highline = min(lineno + options.line_context, highline)
            highline = max(lineno, highline)
        for lno in range(lowline, highline + 1):
            line = linecache.getline(filename, lno, frame.f_globals)
            if line:
                self.lines[lno] = line.rstrip()

    def clear(self):
        """
        Ensure that all the variables are cleared so that we do not hold any
        recursive references.
        """
        # Actually we haven't held on to any references at present, so this
        # isn't strictly necessary, but it will make things easier if we do.
        # We convert the lines list into a single string, which takes up
        # less room.
        if self.lines:
            newlines = SparseList()
            newlines[self.lineno] = self.lines[self.lineno]
            self.lines = newlines

    def __str__(self):
        if self.lines[self.lineno] is None:
            return ''
        return self.lines[self.lineno].strip()

    def __getitem__(self, key):
        return self.lines[key]

    def __iter__(self):
        return self.lines.__iter__()

    def __getattr__(self, name):
        """
        Make this object work like a string; proxy all the string methods
        through to the string methods.
        """
        if hasattr(str, name):
            return getattr(str(self), name)

        raise AttributeError("No attribute '%s' on LineFrame object" % (name,))


def extract_tb(tb, limit=None):
    """
    Extract the traceback information into simple format - with more
    information about the content.

    Return a list of up to limit "pre-processed" stack trace entries
    extracted from the traceback object tb. It is useful for alternate
    formatting of stack traces. If limit is omitted or None, all entries
    are extracted. A "pre-processed" stack trace entry is a 4-tuple
    (filename, line number, function name, text) representing the
    information that is usually printed for a stack trace. The text is a
    string with leading and trailing whitespace stripped; if the source
    is not available it is None.

    The tuple is accessible by name using the properties:
        - `filename`
        - `lineno`
        - `name`
        - `line`
        - `locals` (which at pesent will remain None for compatibility
          with Python 2)

    To retain the old behaviour, and still be useful as a means of
    extending the content, we encapsulate the function in an object whose
    string representation is still the function, but which can also
    contain more information about the context.

    In the new API, function name and line are both objects.

      - Function name:
        - Stringifies to the function name and parameters.
        - Member 'full_name' contains the function name.
        - Member 'params' contains a string of the parameters as passed.
        - Member 'param_names' contains a list of the parameter names.
        - Member 'param_declaration' contains a list of the parameter declarations.
        - Member 'locals' contains a dictionary of local variables.
        - Member 'changed_variables' contains a dictionary keyed by the
              names of variables which may be changed since the start
              of the function. The value is a list of dictionaries
              containing the type of change, and the line it occurs on.
              The list may be incomplete (it is inferred from the source)
      - Line:
        - Stringifies to the stripped content of the source line.
        - Member 'lines' contains a list of tuples containing the lines
              leading up to the source line in the form (line number,
              text). The lines are not stripped.
        - Iterating, or reading as list will return the lines in order.
    """

    if not options.enable or not options.enable_extract:
        return traceback_extract_tb(tb, limit)

    extract_info = []

    # Same rules as the 'traceback' module for the default limit
    if limit is None:
        if hasattr(sys, 'tracebacklimit'):
            limit = sys.tracebacklimit  # pylint: disable=E1101

    tb_list = []
    while tb is not None:
        tb_list.append(tb)
        tb = tb.tb_next

    tb_list = options.filter_frames(tb_list)

    for tb in tb_list:
        # We allow there to be a check whether the frame can be ignored
        if not options.ignore_frame(tb):
            frame = tb.tb_frame
            lineno = tb.tb_lineno

            code = frame.f_code
            filename = code.co_filename

            # Create the new object for this function
            function = FunctionFrame(frame)
            lines = LineFrame(tb)

            extract_info.append(FrameSummary(filename, lineno, function, lines))

            if limit is not None:
                limit -= 1
                if limit <= 0:
                    break

    return extract_info


def extract_stack(f=None, limit=None):
    """Extract the raw traceback from the current stack frame.

    The return value has the same format as for extract_tb().  The
    optional 'f' and 'limit' arguments have the same meaning as for
    print_stack().  Each item in the list is a quadruple (filename,
    line number, function name, text), and the entries are in order
    from oldest to newest stack frame.
    """
    if f is None:
        try:
            raise ZeroDivisionError
        except ZeroDivisionError:
            # Skip our own frame entry
            f = sys.exc_info()[2].tb_frame.f_back

    # Same rules as the 'traceback' module for the default limit
    if limit is None:
        if hasattr(sys, 'tracebacklimit'):
            limit = sys.tracebacklimit  # pylint: disable=E1101

    extract_info = []
    while f is not None:

        # NOTE: No check whether the frame can be ignored.
        lineno = f.f_lineno
        code = f.f_code
        filename = code.co_filename

        # Create the new object for this function
        function = FunctionFrame(f)
        lines = LineFrame(f)

        extract_info.append(FrameSummary(filename, lineno, function, lines))

        f = f.f_back

        if limit is not None:
            limit -= 1
            if limit <= 0:
                break

    extract_info.reverse()
    return extract_info


def format_file_header(filename, lineno, function, indent=2):
    """
    Return a list of lines representing the message about the function that was
    called. Includes the list of parameter variables, if configured.
    """
    row_lines = []
    name = function
    list_params = False
    if isinstance(function, FunctionFrame):
        name = StyledString(function.full_name, style='function-name')
        if options.params_inline == 'none':
            list_params = True
        elif options.params_inline == 'prototype':
            list_params = True

            def paramify(param):
                if isinstance(param, list):
                    return '(' + _join_list(param, ', ', add_newline=False) + ')'
                return StyledString(param, style='varname')
            params = [paramify(param) for param in function.param_declaration]
            name = StyledString("{}({})").format(name, StyledString(_join_list(params, ', ', add_newline=False),
                                                                    style='prototype-parameters'))
        elif options.params_inline == 'inline':
            list_params = False
            name = StyledString('{}{}').format(name, function.params_styled)

        if options.show_function_type:
            name = StyledString("{}  [{}]").format(name, StyledString(function.type, style='function-type'))

    trail = ''
    if name is not None:
        trail = StyledString(", in {}").format(name)
    row_lines.append((' ' * indent) +
                     StyledString("File '{}', line {}{}", style='header.file').format(
                         StyledString(presentation_filename(filename), style='filename'),
                         StyledString(lineno, style='lineno'),
                         trail) +
                     "\n")

    if list_params:
        variables, order = function.params_as_variables()
        if variables:
            if options.header_on_parameters:
                indent += 2
                row_lines.append((' ' * indent) +
                                 StyledString(options.parameters_message, style="header.parameters"))
            varlines = longtraceback.Variables.format_variables(variables,
                                                                indent=indent + 2,
                                                                order=order,
                                                                style='parameter')
            row_lines.extend(varlines)

    return row_lines


def format_list(extracted, styled=True):
    """
    Given a list of tuples as returned by extract_tb() or
    extract_stack(), return a list of strings ready for printing. Each
    string in the resulting list corresponds to the item with the same
    index in the argument list. Each string ends in a newline; the
    strings may contain internal newlines as well, for those items whose
    source text line is not None.
    """

    if not options.enable or not options.enable_format:
        return traceback_format_list(extracted)

    output_lines = []

    def quantise_extracted_info(filename, lineno, function):
        func_name = function
        if isinstance(function, FunctionFrame):
            func_name = function.full_name

        if options.show_parameter_changes_on_repetitions:
            # In order to find repetitions, we don't include the function parameters
            key = (filename, lineno, func_name, '')
        else:
            if isinstance(function, FunctionFrame):
                key = (filename, lineno, func_name, function.params)
            else:
                key = (filename, lineno, func_name, '')

        return key

    function = None
    lines = None

    last_seen_params = []
    last_seen = quantise_extracted_info('', -1, None)
    last_seen_count = 0

    def check_repetitions():
        if not options.recognise_repetitions:
            return

        if last_seen_count > 1:
            row_lines = []
            row_lines.append("  " +
                             StyledString(options.frame_repetition_message.format(last_seen_count - 1),
                                          style='header.frame-repeated'))

            if options.show_parameter_changes_on_repetitions:
                # Check which of the parameters changed between frames
                first_function = last_seen_params[0][2]
                if isinstance(first_function, FunctionFrame):
                    first_vars, order = first_function.params_as_variables(expand_args=True)

                    # Create list of the parameters for each variable
                    try:
                        changing_vars = dict((key, longtraceback.DescribeSequence.DescribeSequence([value]))
                                             for key, value in first_vars.items())
                    except Exception as ex:  # pylint: disable=broad-except
                        internal_exception("Sequence of repeated parameters", ex)
                        changing_vars = dict((key, [value])
                                             for key, value in first_vars.items())
                    for params in last_seen_params[1:]:
                        function = params[2]
                        function_vars, _ = function.params_as_variables(expand_args=True)
                        for name, value in function_vars.items():
                            if name in changing_vars:
                                changing_vars[name] += value
                            else:
                                # not a known variable
                                # We want to insert the variable into the existing order in an appropriate place.
                                pass  # FIXME

                    if order:
                        longest = max(len(name) for name in order)
                        for name in order:
                            param = StyledString("{1:{0}} := {2}").format(longest,
                                                                          StyledString(name, style='varname'),
                                                                          StyledString(changing_vars[name].describe(),
                                                                                       style='sequence-values'))
                            row_lines.append("    " +
                                             StyledString(param, style='parameter-sequence'))

            if options.blank_line_between_frames:
                row_lines.append("")

            output_lines.append(_join_list(row_lines))

    for filename, lineno, function, lines in extracted:
        row_lines = []
        try:
            if options.recognise_repetitions:
                seen = quantise_extracted_info(filename, lineno, function)
                if seen == last_seen:
                    # This is the same as the prior line
                    last_seen_count += 1
                    last_seen_params.append((filename, lineno, function, lines))
                    continue
                else:
                    # We need to state that we've repeated a line (if we have)
                    check_repetitions()
                    last_seen_count = 1

                last_seen = seen
                last_seen_params = [(filename, lineno, function, lines)]

            # The file header line includes the parameters, if necessary.
            row_lines.extend(format_file_header(filename, lineno, function, indent=2))

            row_lines.extend("    " + line for line in annotate_lines(lines, lineno, None))

            if filename not in ('<stdin>', '<console>') and isinstance(function, FunctionFrame):
                # We only care about the locals if this isn't a command line (and it's one of our objects)
                def ignored(name, value):
                    """
                    Ignore the variable if it was a parameter
                    """
                    if options.params_inline != 'inline' and name in function.param_names:
                        return True
                    return longtraceback.Variables.ignored_local_variable(name, value)

                varlines = longtraceback.Variables.format_variables(function.locals,
                                                                    ignore=ignored,
                                                                    indent=4,
                                                                    style='local')
                if varlines:
                    if options.header_on_locals:
                        row_lines.append("    " + StyledString(options.locals_message, style='header.locals'))
                        row_lines.extend(["  " + line for line in varlines])
                    else:
                        row_lines.extend(varlines)

                extensions = function.extensions
                if extensions:
                    row_lines.extend(_format_extensions(extensions, indent=4))

            if options.blank_line_between_frames:
                row_lines.append("")

            output_lines.append(_join_list([row.rstrip() + '\n' for row in row_lines], add_newline=False))

        except Exception as ex:  # pylint: disable=W0703
            internal_exception("Processing traceback", ex)
            output_lines.append(None)

    # Any repetitions of the last line need to be reported
    check_repetitions()

    # We have a set of output lines; some of which may have failed in their
    # conversion through our routines, and if so we want to fall back to the old
    # base python traceback so that we still get some output.
    old_output_lines = None
    for index, line in enumerate(output_lines):
        if line is None:
            if old_output_lines is None:
                old_output_lines = traceback_format_list(extracted)
            output_lines[index] = old_output_lines[index]

    # Clear the last seen parameters in case there's anything left there to cause reference loops
    last_seen_params = None
    # And clear the values from the extracted list
    for filename, lineno, function, lines in extracted:
        # If it was our traceback structure, we must clear it to prevent reference loops
        if hasattr(function, 'clear'):
            function.clear()
        if hasattr(lines, 'clear'):
            lines.clear()

    if styled:
        output_lines = [str(line) for line in output_lines]

    return output_lines


def _format_extensions(extensions, indent=0):
    """
    Format the output from any of the traceback extensions.

    Returns a list of lines generated by the extensions properties in the fields.
    """

    indent_with = ' ' * indent

    lines = []
    for section in extensions:

        section_name = section['section']
        style = section.get('style', 'extensions.%s' % (section_name.lower(),))
        fields = section.get('fields', {})

        lines.append(indent_with + StyledString('%s:' % (section_name,),
                                                style='header.%s' % (style,)))
        for content in section.get('content', []):
            lines.append(indent_with + "  " + StyledString(content, style=style))

        varlines = longtraceback.Variables.format_variables(fields, ignore=None, indent=indent + 2, style=style)
        lines.extend(varlines)

    return lines


def _format_final_exc_line(etype, value):
    """
    Return a list of a single line -- normal case for format_exception_only
    """
    valuestr = _safe_string(value)
    if value is None or not valuestr:
        line = StyledString(etype, style='exception-name')
    else:
        line = StyledString(etype, style='exception-name') + ": " + \
               StyledString(valuestr, style='exception-message')
    return StyledString(line, style='header.exception') + "\n"


def _safe_string(val):
    """
    Make a safe, printable, string from an object or string.
    """
    try:
        return str(val)
    except Exception:  # pylint: disable=W0703
        pass

    try:
        unistr = unicode(val)
        return unistr.encode("ascii", "backslashreplace")
    except Exception:  # pylint: disable=W0703
        pass

    return '<unprintable %s object>' % (type(val).__name__,)


def annotate_lines(source_lines, lineno, char_offset):
    """
    Annotate lines with numbers, add any other indications, like the fault position.

    @param source_lines:    List of source code lines, a single line, or a LineFrame object
    @param filename:        Filename that these lines came from
    @param lineno:          Line number to reference in the source_lines
    @param char_offset:     Offset in the line of any error (or None for no specific point)
    """
    lines = []

    last_line = None
    if isinstance(source_lines, (LineFrame, list)):
        # Generate a context if this is a list of lines
        first = max(1, lineno - options.line_context)
        last = lineno
        for lno, line in enumerate(source_lines[first:last + 1], start=first):
            if line is None:
                continue
            text = StyledString("{:>5}{:2} {}").format(StyledString(lno, style='line-number'),
                                                       StyledString('->' if lno == lineno else ' :',
                                                                    style='line-divider'),
                                                       StyledString(line, style='source'))
            if lno == lineno:
                text = StyledString(text, style='line-exception')
            lines.append(text)
            last_line = line
    else:
        # Otherwise, just show the single line supplied
        text = StyledString("{:>5}{:2} {}").format(StyledString(lineno, style='line-number'),
                                                   StyledString('->', style='line-divider'),
                                                   StyledString(source_lines, style='source'))
        lines.append(text)
        last_line = lines

    if char_offset is not None and last_line is not None:
        caretspace = last_line
        offset = min(len(caretspace), char_offset) - 1
        # non-space whitespace (likes tabs) must be kept for alignment
        caretspace = ((c if c.isspace() else ' ') for c in caretspace[:offset])
        text = StyledString("{:>5}{:2} {}{}").format("", "", ''.join(caretspace),
                                                     StyledString('^', style='context-caret'))
        lines.append(text)

    return lines


@apply_styling
def format_exception_only(exc_class, exc):
    """
    Format the exception information into a list of lines to report.

    @note: We violate the rule that the 'format_exception_only' call's last list item
           is the exception line.
    """

    # Special cases for raised exceptions which are not the expected
    # types:
    if (not inspect.isclass(exc_class) or
            exc_class is None or
            isinstance(exc_class, basestring)):
        return [_format_final_exc_line(exc_class, exc)]

    stype = exc_class.__name__

    if not issubclass(exc_class, SyntaxError):
        lines = traceback_format_exception_only(exc_class, exc)
    else:
        # Syntax error, so try to provide more information
        lines = []
        try:
            _, (filename, lineno, offset, badline) = exc.args
        except Exception:  # pylint: disable=W0703
            pass
        else:
            filename = filename or "<string>"
            # The file header line includes the parameters, if necessary.
            lines.extend(format_file_header(filename, lineno, None, indent=2))
            if badline is not None:

                # Initially, we'll say that the source lines is just the line supplied
                source_lines = SparseList()
                source_lines[lineno] = badline.rstrip('\n')

                # But if it is a real file, we can give more context
                if filename[0] != '<' and filename[1] != '>':
                    linecache.checkcache(filename)

                    # Only include the extra line context if the line given is the one in the file.
                    if badline == linecache.getline(filename, lineno, globals()):
                        lowline = max(1, lineno - options.line_context)
                        for lno in range(lowline, lineno + 1):
                            line = linecache.getline(filename, lno, globals())
                            if line:
                                source_lines[lno] = line.rstrip()

                lines.extend(["    " + StyledString(inline, style='context') + "\n"
                              for inline in annotate_lines(source_lines, lineno, offset)])

        lines.append(_format_final_exc_line(stype, exc))

    # Only print the members if this is an exception.
    # Omit SyntaxErrors as all the information has already been provided.
    if isinstance(exc, BaseException) and not isinstance(exc, SyntaxError):
        exc_names = [name for name in dir(exc)
                     if not name.startswith('__') and
                     name not in ('args', 'message', 'print_file_and_line', 'with_traceback')]
        if exc_names:
            lines.append("  " + StyledString("Exception properties:", style='header.exception.properties') + "\n")
            try:
                exc_vars = dict([(name, getattr(exc, name, InvalidAttribute(exc, name))) for name in exc_names])
                varlines = longtraceback.Variables.format_variables(exc_vars,
                                                                    order=sorted(exc_names),
                                                                    indent=4,
                                                                    style='exception')
                for line in varlines:
                    lines.append(line + "\n")
            except Exception as ex:  ## pylint: disable=broad-except
                internal_exception('Handling exception properties', ex)

    return lines


def print_list(extracted, file=None, header=''):  ## pylint: disable=redefined-builtin
    """
    Print stack list.

    Print the list of tuples as returned by extract_tb() or
    extract_stack() as a formatted stack trace to the given file.
    """
    if file is None:
        file = sys.stderr

    lines = format_list(extracted, styled=True)
    if lines and header:
        print(header, file=file)

    for line in lines:
        if line.endswith('\n'):
            line = line[:-1]
        print(line, file=file)


def print_tb(trace, limit=None, file=None, header=''):  ## pylint: disable=redefined-builtin
    """
    Print up to limit stack trace entries from traceback.

    If limit is omitted or None, all entries are printed. If file is omitted or None, the output goes to sys.stderr;
    otherwise it should be an open file or file-like object to receive the output.
    """
    if file is None:
        file = sys.stderr

    lines = format_list(extract_tb(trace, limit=limit), styled=True)
    if lines and header:
        print(header, file=file)
    for line in lines:
        if line.endswith('\n'):
            line = line[:-1]
        print(line, file=file)


def print_exception(exc_class, exc, trace, limit=None, file=None, chain=True):  ## pylint: disable=redefined-builtin
    """
    Print exception information and up to limit stack trace entries from traceback to file.

    This differs from print_tb() in the following ways:
        - if traceback is not None, it prints a header Traceback (most recent call last):
        - it prints the exception type and value after the stack trace
        - if type is SyntaxError and value has the appropriate format, it prints the line where the syntax error
          occurred with a caret indicating the approximate position of the error.
    """
    if file is None:
        file = sys.stderr

    if trace is None:
        # Python 3.4 'code' module passes None as trace, when the sys.excepthook is set - which it is
        # when we are using the longtraceback system. So we need to restore the traceback if this is
        # the case.
        _, _, trace = sys.exc_info()

    # Output the chaining messages
    if chain:
        if getattr(exc, '__cause__', None) is not None:
            print_exception(type(exc.__cause__),
                            exc.__cause__,
                            exc.__cause__.__traceback__,
                            chain=True,
                            limit=limit,
                            file=file)
            print("\n" +
                  StyledString(options.cause_message, style='header.cause') +
                  "\n", file=file)
        elif getattr(exc, '__context__', None) is not None and \
             not getattr(exc, '__suppress_context__', False):
            print_exception(type(exc.__context__),
                            exc.__context__,
                            exc.__context__.__traceback__,
                            chain=True,
                            limit=limit,
                            file=file)
            print("\n" +
                  StyledString(options.context_message, style='header.context') +
                  "\n", file=file)

    if trace:
        # Include a blank line first, to try to clear up the start of the message
        print_tb(trace, limit, file,
                 header="\n" + StyledString(options.start_message, style='header.traceback'))

    for line in format_exception_only(exc_class, exc):
        print(line.rstrip(), file=file)


def format_exception(exc_class, exc, trace, limit=None, chain=True):
    """
    Format a stack trace and the exception information.

    The arguments have the same meaning as the corresponding arguments to print_exception().
    The return value is a list of strings, each ending in a newline and some containing internal newlines.
    When these lines are concatenated and printed, exactly the same text is printed as does print_exception().
    """
    output = IOClass.StringIO()
    print_exception(exc_class, exc, trace, limit=limit, file=output, chain=chain)
    value = output.getvalue()
    output.close()
    return value.splitlines(True)


def activate():
    """
    Enable the use of the longtraceback system.
    """
    sys.excepthook = print_exception
    traceback.extract_stack = extract_stack
    traceback.extract_tb = extract_tb
    traceback.format_list = format_list
    traceback.format_exception = format_exception
    traceback.print_exception = print_exception
    traceback.print_tb = print_tb
    traceback.print_list = print_list
    traceback.format_exception_only = format_exception_only
    traceback._format_final_exc_line = _format_final_exc_line  # pylint: disable=protected-access


def deactivate():
    """
    Disable the use of the longtraceback system.
    """
    sys.excepthook = sys_excepthook
    traceback.extract_stack = traceback_extract_stack
    traceback.extract_tb = traceback_extract_tb
    traceback.format_list = traceback_format_list
    traceback.format_exception = traceback_format_exception
    traceback.print_exception = traceback_print_exception
    traceback.print_tb = traceback_print_tb
    traceback.print_list = traceback_print_list
    traceback.format_exception_only = traceback_format_exception_only
    traceback._format_final_exc_line = traceback_format_final_exc_line  # pylint: disable=protected-access


activate()
