#!/usr/bin/env python
"""
Class to provide dumping of variables in a more structured manner.
"""

import inspect
import re

from .ReduceFilename import presentation_filename


# Ensure that we can check basestring on Python 2 and 3.
try:
    basestring
except NameError:
    basestring = str  # pylint: disable=redefined-builtin


class FormatOptions(object):

    def __init__(self):

        # The limits on the string formatting
        self.string_max_len = 1024 * 4
        self.string_max_lines = 8

        # The limits on the list formatting
        self.list_max_items = 8

        # The limits on the dict formatting
        self.dict_max_keys = 8

        # The limits on the set formatting
        self.set_max_items = 8

        # Whether we hide the instance and object ids
        self.hide_instance_ids = True

        # Whether we show simple properties of objects.
        self.show_simple_object_properties = True

        # Which members of which builtin objects will be displayed.
        # The key's presence indicates that we will include members for that builtin.
        # The value may be None (to just display default members, or an iterable containing
        # a list of elements that we force the display of.
        self.formatable_builtin_members = {
            'functools.partial': ('func',)
        }

        # Whether we report on failures to produce variable output
        self.debug_vars = True


options = FormatOptions()


def formatable_members(value):
    """
    Return the members of a given object which are presentable to the user.

    @param value:   The value we wish to know about

    @return:        A list of the property names which are user presentable
    """
    extra = []

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
        if fullname in options.formatable_builtin_members:
            ok = True
            extra = options.formatable_builtin_members[fullname] or []

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

    members = [member for member in dir(value)
               if member in extra or is_formatable_member(member, getattr(value, member, None))]

    return members


class ValueItems(object):

    def __init__(self, items=None,
                 name='item', plural=None,
                 itemprefix=None, itemsuffix=None, itemseparator=', ',
                 itemelementprefix=None, itemelementsuffix=None, itemelementseparator=None,
                 prefix='', suffix=''):

        self.items = items or []
        self.name = name
        self.plural = plural or name + 's'
        # items are the individual indexed values (or similar) related to the value
        self.itemprefix = itemprefix
        self.itemsuffix = itemsuffix if itemsuffix is not None else itemprefix
        self.itemseparator = itemseparator
        # itemelements are the constituents of the items provided, usually key/value pairs
        self.itemelementprefix = itemelementprefix
        self.itemelementsuffix = itemelementsuffix if itemelementsuffix is not None else itemelementprefix
        self.itemelementseparator = itemelementseparator or None
        # the prefix and suffix is applied around the list of items
        self.prefix = prefix
        self.suffix = suffix
        self.trailer = ''
        self.extra = 0
        self._itemelementwidth = None

    def _element_width(self):
        if self.itemelementseparator is None:
            return None
        else:
            if self._itemelementwidth is None:
                if self.items:
                    self._itemelementwidth = max(len(ekey) for ekey, _ in self.items)
                else:
                    self._itemelementwidth = 0
            return self._itemelementwidth

    def __str__(self):
        content = []
        items = self.items
        if self.itemelementseparator is not None:
            # FIXME: Apply element_width?
            items = ["%s%s%s%s%s" % (self.itemelementprefix or '', ekey,
                                     self.itemelementseparator, evalue,
                                     self.itemelementsuffix or '') for (ekey, evalue) in items]

        items = [self.itemseparator.join("%s%s%s" % (self.itemprefix or '',
                                                     item,
                                                     self.itemsuffix or '') for item in items)]

        if self.extra:
            extra = " +%s" % (self.extra)
            if self.name:
                extra += " %s" % (self.name if self.extra == 1 else self.plural,)
            items.append(extra)

        if self.trailer:
            items.append(self.trailer)

        if self.prefix or self.suffix:
            content = [self.prefix] + items + [self.suffix]
        else:
            content = items

        if len(content) == 1:
            return content[0]

        return "".join(content)

    def __iadd__(self, other):
        if self.itemelementseparator is not None:
            self._itemelementwidth = None

        self.items.append(other)
        return self

    def __add__(self, other):
        return ValueItems(items=self.items + other,
                          name=self.name, plural=self.plural,
                          itemprefix=self.itemprefix, itemsuffix=self.itemsuffix, itemseparator=self.itemseparator,
                          itemelementprefix=self.itemelementprefix, itemelementsuffix=self.itemelementsuffix,
                          itemelementseparator=self.itemelementseparator,
                          prefix=self.prefix, suffix=self.suffix)

    def __len__(self):
        return len(self.items)

    def append(self, value):
        self += value
        return self

    def extend(self, values):
        if self.itemelementseparator is not None:
            self._itemelementwidth = None

        self.items.extend(values)
        return self

    def set_trailer(self, trailer):
        self.trailer = trailer

    def set_extra(self, extra):
        self.extra = extra

    def set_name(self, name='item', plural=None):
        self.name = name
        self.plural = plural or name + 's'


def find_formatters_by_mro(value):
    formatters = []

    globals_dict = globals()
    mro = inspect.getmro(value.__class__)

    for value_class in mro:
        value_clsname = value_class.__name__
        if value_clsname == 'object':
            continue

        if value_clsname.islower():
            value_clsname = value_clsname.capitalize()
        value_attrname = 'Format' + value_clsname

        if value_attrname in globals_dict:
            value_cls = globals_dict[value_attrname]
            formatters.append((value_clsname, value_cls(value)))

    if not formatters:
        formatters.append(('object', FormatObject(value)))

    return formatters


class ValueFormat(object):
    formatter_finders = [
        find_formatters_by_mro
    ]

    def __init__(self, value):
        self.value = value
        self._items = None
        self.formatters = []
        for formatter_finder in ValueFormat.formatter_finders:
            formatters = formatter_finder(value)
            self.formatters.extend(formatters)

    @property
    def items(self):
        if self._items is None:
            items = []
            for formatter in self.formatters:
                elements = formatter[1]()
                if isinstance(elements, list):
                    items.extend(elements)
                else:
                    items.append(elements)
            self._items = items
        return self._items

    def __str__(self):
        return "\n".join("%s" % (item,) for item in self.items)


class BaseFormat(object):

    def __init__(self, value):
        self.value = value

    def __call__(self):
        return repr(self.value)

    def __str__(self):
        return str(self())

    def is_default_func(self, func_name, on_class=object):
        value_class = getattr(self.value, '__class__', None)
        if value_class:
            value_func = getattr(value_class, func_name, None)
            if value_func is getattr(on_class, func_name):
                return True

        value_func = getattr(self.value, func_name, None)
        if value_func is getattr(on_class, func_name):
            return True

        return False

    def debug_exception(self, msg, ex):
        if options.debug_vars:
            try:
                print("%s: %s : %s" % (msg, self.value, type(self.value)))
            except Exception:  # pylint: disable=broad-except
                print("%s: <<failed>> : %s" % (msg, type(self.value,)))
            print("Exception: %r" % (ex,))

    def hide_instance_ids(self, value):  # pylint: disable=no-self-use
        """
        Remove any 'object at 0x1231245' type messages from within a value.
        """
        value = re.sub(r' (object|instance) at (0x[0-9a-fA-F]{8,}|[0-9]+)', ' \\1', value)
        value = re.sub(r' at 0x[0-9a-fA-F]{8,}>', '>', value)
        return value


class NoDedicatedReprError(Exception):
    pass


class NoDedicatedStrError(Exception):
    pass


class FormatObject(BaseFormat):

    def typename(self):
        try:
            # This actually does not report the correct class nesting, but it's consistent between
            # versions. Eventually we may do a more complex search for such objects.
            class_name = "%s.%s" % (self.value.__class__.__module__, self.value.__class__.__name__)
            return "<%s object>" % (class_name,)

        except Exception as ex:  ## pylint: disable=broad-except
            # Failures, or unrecogniseable objects are handled the same way.
            # (except that we report exceptions)
            self.debug_exception("Failed typename evaluation whilst formatting variable", ex)

        return type(self.value)

    def __call__(self):
        """
        Format a general object.
        """
        items = ValueItems(name='value',
                           itemprefix='', itemsuffix='', itemseparator=', ')
        failing = []
        try:
            if getattr(self.value.__class__, '__repr__') == object.__repr__:
                raise NoDedicatedReprError()
            failing.append('repr')
            value = repr(self.value)
        except Exception as ex:  # pylint: disable=broad-except
            if 'repr' in failing:
                self.debug_exception("Failed repr evaluation whilst formatting variable", ex)
            try:
                if getattr(self.value.__class__, '__str__') == object.__str__:
                    raise NoDedicatedStrError()
                failing.append('str')
                value = str(self.value)
            except Exception as ex:  # pylint: disable=W0703
                if 'str' in failing:
                    self.debug_exception("Failed str evaluation whilst formatting variable", ex)
                if failing:
                    value = "%s (failed %s)" % (self.typename(), "/".join(failing))
                else:
                    value = self.typename()

        # Make the content a little less spammy by removing the object/instance information
        if options.hide_instance_ids:
            value = self.hide_instance_ids(value)

        # Make 'type' and 'class' identical (they are in Python 3 and to all intents and purposes
        # there is no difference).
        if value.startswith('<type '):
            value = '<class %s' % (value[6:],)

        items += value

        # Now see if we have any properties we may present
        if options.show_simple_object_properties:
            members = formatable_members(self.value)
            if members:
                property_items = ValueItems(name='property', plural='properties',
                                            itemprefix='.', itemsuffix='', itemseparator=', ',
                                            itemelementprefix='', itemelementsuffix='',
                                            itemelementseparator=' = ')
                for member in members:
                    property_items += (member, getattr(self.value, member, None))

                return [items, property_items]

        return items


class FormatStr(BaseFormat):

    def __call__(self):
        """
        Format a string, limiting its output.
        """
        string = self.value

        if '\n' in string or '\r' in string:
            items = ValueItems(name='line', itemprefix='"', itemseparator=' ')

            lines = string.splitlines(True)
            if len(lines) > options.string_max_lines or \
               len(self.escape_string(string)) + len(lines) > options.string_max_len:
                num_lines = len(lines)
                lines = lines[0:options.string_max_lines]
                # accumulated length, accounting for no leading space on first line
                len_so_far = -1
                for line in lines:
                    escaped = self.escape_string(line)
                    len_so_far += len(escaped) + 1  # plus a separating space
                    if len_so_far != 0 and len_so_far > options.string_max_len:
                        break
                    items += escaped

                more_lines = num_lines - len(items)
                items.set_extra(more_lines)
            else:
                for line in lines:
                    items += self.escape_string(line)
            return items

        items = ValueItems(name='character', itemprefix='"', itemseparator=' ')
        if len(string) > options.string_max_len:
            full_len = len(string)
            string = string[0:options.string_max_len]
            items.set_extra(full_len - options.string_max_len)
        items += self.escape_string(string)

        return items

    @staticmethod
    def escape_string(string):
        string = string.replace('\\', '\\\\')
        string = string.replace('"', '\\"')
        string = string.replace('\t', '\\t')
        string = string.replace('\r', '\\r')
        string = string.replace('\n', '\\n')
        return string


class FormatFunction(BaseFormat):

    def __call__(self):
        items = ValueItems(name='function')
        if hasattr(self.value, 'compat_co_firstlineno'):
            lineno = self.value.compat_co_firstlineno
        else:
            lineno = getattr(self.value.__code__, 'co_firstlineno', None)

        value = str(self.value)
        # Make the content a little less spammy by removing the object/instance information
        if options.hide_instance_ids:
            value = self.hide_instance_ids(value)

        if value.startswith('<unbound method '):
            value = '<function %s' % (value[16:],)

        filename = getattr(self.value.__code__, 'co_filename', None)
        msg = value
        if filename is not None:
            msg += " in '%s'" % (presentation_filename(filename),)
        if lineno is not None:
            msg += " at line %s" % (lineno,)

        items += msg

        return items


class FormatList(BaseFormat):

    def __call__(self):
        prefix = self.value.__class__.__name__ + '('
        suffix = ')'
        if self.value.__class__ is list:
            prefix = '['
            suffix = ']'
        elif self.value.__class__ is tuple and len(self.value) > 1:
            prefix = '('
            suffix = ')'
        elif isinstance(self.value, (list, tuple)):
            prefix += '['
            suffix = ']' + suffix

        items = ValueItems(name='item',
                           itemseparator=', ',
                           prefix=prefix, suffix=suffix)
        values = self.value
        if len(values) > options.list_max_items:
            items.set_extra(len(values) - options.list_max_items)
            values = values[:options.list_max_items]

        items.extend([ValueFormat(value) for value in values])

        return items

FormatTuple = FormatList


class FormatSet(BaseFormat):

    def __call__(self):
        label = self.value.__class__.__name__
        items = ValueItems(name='member',
                           itemseparator=', ',
                           prefix=label + '([', suffix='])')
        values = self.value

        # If the content is entirely one of the simple types, we can sort it
        # without worrying too much.
        if all(isinstance(item, (int, float, basestring)) for item in values):
            try:
                values = sorted(values)
            except Exception as ex:  # pylint: disable=broad-except
                self.debug_exception("Failed sorting whilst formatting variable", ex)

        if len(values) > options.set_max_items:
            items.set_extra(len(values) - options.set_max_items)
            values = values[:options.set_max_items]

        items.extend([ValueFormat(value) for value in values])

        return items

FormatFrozenset = FormatSet


class FormatDict(BaseFormat):

    def __call__(self):
        items = ValueItems(name='pair',
                           itemseparator=', ',
                           itemelementseparator=': ',
                           prefix='{', suffix='}')

        keys = self.value.keys()
        try:
            keys = sorted(keys)
        except Exception as ex:  # pylint: disable=broad-except
            self.debug_exception(ex, "Failed sorting whilst formatting variable")

        if len(keys) > options.dict_max_keys:
            items.set_extra(len(keys) - options.dict_max_keys)
            keys = keys[:options.dict_max_keys]
        items.extend((ValueFormat(ekey), ValueFormat(self.value[ekey])) for ekey in keys)

        return items


class FormatBaseException(BaseFormat):

    def __call__(self):
        items = ValueItems(name='fields',
                           itemseparator=', ',
                           itemelementprefix='.', itemelementsuffix='', itemelementseparator='=',
                           prefix='', suffix='')

        exc_names = sorted([name for name in dir(self.value)
                            if not name.startswith('__') and
                            name not in ('args', 'message', 'print_file_and_line', 'with_traceback')])
        if exc_names:
            items.extend((ekey, ValueFormat(getattr(self.value, ekey))) for ekey in exc_names)

        return items


FormatInstancemethod = FormatFunction
FormatMethod = FormatFunction
