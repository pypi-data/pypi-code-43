#!/usr/bin/env python
"""
Handling of variables within the traceback operations.
"""

import inspect
import math
import re
import types

from longtraceback.ReduceFilename import presentation_filename
import longtraceback.Styling
import longtraceback.ValueFormat as ValueFormat


# Ensure that we can check basestring and unicode on Python 2 and 3.
try:
    basestring
except NameError:
    basestring = str  # pylint: disable=redefined-builtin

try:
    unicode
except NameError:
    unicode = str  # pylint: disable=redefined-builtin

# Similarly for the 'long' type which does not exist in Python 3
try:
    long
except NameError:
    long = int  # pylint: disable=redefined-builtin


# Constructor for the StyledString
StyledString = longtraceback.Styling.StyledString



def ignored_local_variable(name, value):
    """
    Decide whether we ignore a local variable from the traceback.

    We need to avoid reporting on certain things so that we do not end up with
    a long list of locals which hides the useful information about the function.
    """

    if name.startswith('__'):
        return True

    if inspect.isclass(value):
        return True

    module = getattr(value, '__module__', None)
    if module == '__future__':
        return True

    return False


def format_string(string):
    """
    Format a string, limiting its output.

    @param string:  The string to format and limit
    """
    if longtraceback.options.new_value_formatter:
        return str(ValueFormat.ValueFormat(string))

    if '\n' in string or '\r' in string:
        lines = string.splitlines(True)

        if len(lines) < longtraceback.options.string_max_lines and \
           len(string) < longtraceback.options.string_max_len:
            # Simpler case, where the re does not need to be any truncation.
            new_string = []
            for line in lines:
                trail = ''
                while len(line) and line[-1] in '\n\r':
                    trail = ('\\n' if line[-1] == '\n' else '\\r') + trail
                    line = line[:-1]
                new_string.append(format_string(line)[:-1] + trail + '"')

            return " ".join(new_string)

        # Case where we need to truncation the lines
        num_lines = len(lines)
        lines = lines[0:longtraceback.options.string_max_lines]
        new_string = []
        len_so_far = 0
        for line in lines:
            len_so_far += len(line) + 3  # slash n and a separating space
            if len_so_far != 0 and len_so_far > longtraceback.options.string_max_len:
                break
            trail = ''
            while len(line) and line[-1] in '\n\r':
                trail = ('\\n' if line[-1] == '\n' else '\\r') + trail
                line = line[:-1]
            new_string.append(format_string(line)[:-1] + trail + '"')

        more_lines = num_lines - len(new_string)
        return "%s +%s line%s" % (" ".join(new_string), more_lines, 's' if more_lines != 1 else '')

    extra = ''
    if len(string) > longtraceback.options.string_max_len:
        full_len = len(string)
        string = string[0:longtraceback.options.string_max_len]
        extra = " +%s characters" % (full_len - longtraceback.options.string_max_len,)

    string = string.replace('\\', '\\\\')
    string = string.replace('\t', '\\t')
    string = string.replace('\r', '\\r')
    string = string.replace('\x1b', '\\e')
    return '"%s"%s' % (string, extra)


def format_int(value):
    """
    Format an integer, providing a hex representation if possible.

    @param value:  The value to format
    """
    if longtraceback.options.new_value_formatter:
        return str(ValueFormat.ValueFormat(value))

    # msg contains the value and the length to which it should be formatted as a minimum
    msg = [(str(value), 10)]

    if value > 256:
        msg.append(('0x%x' % (value,), 10))

    if value & -value == value and value != 0:
        # There's only 1 bit set.
        bit = int(math.log(value) / math.log(2))
        if bit > 3:
            # Only list bits after bit 3 (ie 16 or higher)
            # FIXME: Make this configurable?
            msg.append(('bit %i' % (bit,), 6))

    if len(msg) == 1:
        return msg[0][0]

    # Format each string to the length requested
    newmsg = []
    for (string, minlen) in msg:
        newmsg.append('{:<{}}'.format(string, minlen))
    return '  '.join(newmsg).strip()


def formatable_members(value):
    """
    Return the members of a given object which are presentable to the user.

    @param value:   The value we wish to know about

    @return:        A list of the property names which are user presentable
    """
    extra = Ellipsis

    if getattr(value, '__module__', '__builtin__') == '__builtin__':
        # Special values for some builtins:
        ok = False
        cls = getattr(value, '__class__', None)
        if cls is None:
            return []
        clsmod = getattr(cls, '__module__', None)
        if clsmod is None:
            return []
        clsname = getattr(cls, '__name__', None)
        if clsname is None:
            return []

        fullname = '.'.join((clsmod, clsname))
        if fullname in longtraceback.options.formatable_builtin_members:
            ok = True
            extra = longtraceback.options.formatable_builtin_members[fullname]

        if not ok:
            return []

    elif inspect.isbuiltin(value):
        return []
    elif inspect.isroutine(value) or inspect.iscode(value) or inspect.isgenerator(value):
        return []
    elif inspect.ismethoddescriptor(value) or inspect.isdatadescriptor(value):
        return []
    elif inspect.istraceback(value) or inspect.isframe(value):
        return []
    elif inspect.isclass(value) or inspect.isabstract(value):
        return []
    elif inspect.ismodule(value):
        return []

    def is_formatable_member(name, value):
        if name.startswith('_'):
            return False
        if inspect.isbuiltin(value):
            return False
        if inspect.isroutine(value) or inspect.iscode(value) or inspect.isgenerator(value):
            return False
        if inspect.ismethoddescriptor(value) or inspect.isdatadescriptor(value):
            return False
        if inspect.istraceback(value) or inspect.isframe(value):
            return False
        if inspect.isclass(value) or inspect.isabstract(value):
            return False
        if inspect.ismodule(value):
            return False

        return True

    members = []
    for member in dir(value):

        if extra is Ellipsis or extra is None:
            # Calling 'getattr' means that we might get exceptions from getters.
            # In this case, we shouldn't allow them to be formatted.
            # It is possible, however, that calling the getter affects the
            # behaviour of the member itself, but at present this means that
            # we cannot always trust this traceback code to not affect the
            # client data.
            try:
                member_value = getattr(value, member, None)
            except Exception:  # pylint: disable=broad-except
                pass
            else:
                if is_formatable_member(member, member_value):
                    members.append(member)
        else:
            # A list of parameters has been supplied, so only include them
            # (if they're presnt)
            if member in extra:
                members.append(member)

    return members


def format_variable(rawval, varname, indent=None):  # pylint: disable=unused-argument
    """
    Format a single variable's value.

    @param rawval:      The raw value to format
    @param varname:     The variable's name, for diagnostics and formatting
    @param indent:      Number of characters to indent by on subsequent lines, or None to not indent

    @return: variable value, with newlines
    """
    val = '<object %s>' % (repr(type(rawval)),)
    try:
        val = '<object %s>' % (rawval.__class__.__name__)

        if rawval is __builtins__:
            val = '<built in functions>'
        elif isinstance(rawval, type):
            val = '<type %s>' % (rawval.__name__,)
        elif isinstance(rawval, (types.FunctionType,
                                 types.MethodType)):
            # Special case for functions
            val = rawval
            if hasattr(val, 'compat_co_firstlineno'):
                lineno = val.compat_co_firstlineno
            else:
                lineno = val.__code__.co_firstlineno
            filename = presentation_filename(val.__code__.co_filename)
            val = StyledString("{} in '{}' at line {}").format(StyledString(str(val), style='function-name'),
                                                               StyledString(filename, style='filename'),
                                                               StyledString(lineno, style='lineno'))
        elif isinstance(rawval, str):
            val = format_string(rawval)
        elif isinstance(rawval, (int, long)) and not isinstance(rawval, bool):
            val = format_int(rawval)
        else:
            if longtraceback.options.new_value_formatter:
                # FIXME: The ValueFormat isn't reliable enough yet.
                val = str(ValueFormat.ValueFormat(rawval))
            else:
                with longtraceback.make_repr_safe():
                    val = repr(rawval)
            if len(val) > longtraceback.options.value_max_len:
                val = val[:longtraceback.options.value_max_len] + " ..."
        if isinstance(val, unicode) and unicode is not str:
            val = val.encode('utf-8')
    except Exception as ex:  # pylint: disable=W0703
        if longtraceback.options.debug_vars:
            longtraceback.internal_exception("getting repr of variable: '%s' : (%s)" % (varname, type(rawval)),
                                             ex, usage='Exception during traceback')
        try:
            val = str(rawval)
        except Exception as ex:  # pylint: disable=W0703
            if longtraceback.options.debug_vars:
                longtraceback.internal_exception("getting str of variable '%s' (%s)" % (varname, type(rawval)),
                                                 ex, usage='Exception during traceback')

    # Make the content a little less spammy by removing the object/instance information
    if longtraceback.options.hide_instance_ids:
        if not isinstance(rawval, basestring):
            try:
                val = re.sub(r' (object|instance) at (0x[0-9a-fA-F]{8,}|[0-9]+)', ' \\1', val)
                val = re.sub(r' at 0x[0-9a-fA-F]{8,}>', '>', val)
                val = re.sub(r' at 0x[0-9a-fA-F]{8,};([^>]+)>', '\\1>', val)
            except Exception as ex:  # pylint: disable=W0703
                if longtraceback.options.debug_vars:
                    longtraceback.internal_exception("failed substitution on variable '%s' (%s)" % (varname,
                                                                                                    type(rawval)),
                                                     ex, usage='Exception during traceback')
                    print("Output was: %r" % (val,))

    return val


def format_variables(localvars, order=None, ignore=None, indent=0, levels=1, style=None):
    """
    Format the variables into a list of lines to print.

    @param localvars:   The local variables dictionary to show
    @param order:       Variables listed in order to show (or None to sort)
    @param ignore:      A function to call to decide if a variable should be ignored.
    @param indent:      Number of characters to indent by
    @param levels:      Number of levels of variables to display
    @param style:       Style to apply to the lines

    @return: list of lines to print
    """
    local_names = [name for name in localvars if ignore is None or not ignore(name, localvars[name])]
    if not local_names:
        return []

    longest = max(len(name) for name in local_names)

    lines = []
    if order is None:
        order = sorted(local_names)

    for varname in order:
        rawval = localvars[varname]
        val = format_variable(rawval, varname, indent=(indent + longest))

        lines.append((' ' * indent) +
                     StyledString("{1:<{0}} = {2}", style=style).format(longest,
                                                                        StyledString(varname, style='varname'),
                                                                        StyledString(val, style='varvalue')))

        if longtraceback.options.show_simple_object_properties and levels > 0:
            members = formatable_members(rawval)
            if members:
                properties = dict([(member, getattr(rawval, member, None)) for member in members])
                more_lines = format_variables(properties, levels=levels - 1, style='property')
                if more_lines:
                    for line in more_lines:
                        lines.append((' ' * (indent + 1)) +
                                     ('.' if line[0] != ' ' else ' ') +
                                     line)

    return lines
