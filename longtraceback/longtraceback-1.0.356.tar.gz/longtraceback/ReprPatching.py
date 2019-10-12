#!/usr/bin/env python
"""
Replace the implementation of 'repr' to allow improved reporting of some types of data.

These patches are only used within the Longtraceback code experimentally, whilst it is
being tested.
"""

import types

bi = globals()['__builtins__']
if isinstance(bi, types.ModuleType):
    bi = bi.__dict__
bi = globals()['__builtins__']
default_repr = None


class ReprPatchBase(object):
    name = 'unknown-patch'

    def __init__(self):
        pass

    def recognise(self, obj):
        """
        Recognise whether this patch can be applied to a given object.

        @param obj:     The object to recognise
        """
        raise NotImplementedError("repr() patching for %s not implemented" % (self.name,))

    def repr(self, obj):
        """
        Return the representation of the object.

        @param obj:     The object to provide the representation of
        """
        raise NotImplementedError("repr() patching for %s not implemented" % (self.name,))


class ReprPatchFunctoolsPartial(object):
    name = 'functools.partial'

    def __init__(self):
        import functools
        dummy_partial = functools.partial(repr)
        self.functools_partial_class = type(dummy_partial)

    def recognise(self, obj):
        return isinstance(obj, self.functools_partial_class)

    @staticmethod
    def repr(obj):
        args_list = ", ".join(repr(arg) for arg in obj.args)
        kw_list = ", ".join('%s=%r' % (key, value) for key, value in obj.keywords.items())
        args = ", ".join(item for item in (repr(obj.func), args_list, kw_list) if item is not None)
        return "functools.partial(%s)" % (args)


class ReprPatchRePattern(object):
    name = '_sre.SRE_Pattern'

    def __init__(self):
        import re
        pattern = re.compile('')
        self.pattern_class = type(pattern)
        self.flag_names = {}
        for name in dir(re):
            if name.isupper() and len(name) > 1:
                self.flag_names[getattr(re, name)] = name

    def recognise(self, obj):
        return isinstance(obj, self.pattern_class)

    def repr(self, obj):
        pattern = obj.pattern
        flags = []
        for flag in sorted(self.flag_names):
            if obj.flags & flag:
                flags.append(self.flag_names[flag])

        flags_label = ' | '.join(flags)
        if flags_label == '':
            flags_label = '0'
        return "<%s(%r, %s)>" % (self.name, pattern, flags_label)


class ReprPatchReMatch(object):
    name = '_sre.SRE_Match'

    def __init__(self):
        import re
        pattern = re.compile('foo(.*)')
        match = pattern.match('foolish')
        self.match_class = type(match)

    def recognise(self, obj):
        return isinstance(obj, self.match_class)

    def repr(self, obj):
        indices = '%s-%s' % (obj.pos, obj.endpos)
        using = obj.re
        groups_list = ', '.join(repr(g) for g in obj.groups())

        return "<%s(%s, matched %s, %s groups: %s)>" % (self.name, repr(using), indices, len(obj.groups()), groups_list)


patch_classes = [
    ReprPatchFunctoolsPartial,
    ReprPatchRePattern,
    ReprPatchReMatch,
]
patches = []


def enable_patch():
    global default_repr     # pylint: disable=global-statement
    global patches          # pylint: disable=global-statement

    if default_repr:
        raise RuntimeError('repr() patching is already enabled')

    # Construct the patch objects for each patch
    patches = [patch() for patch in patch_classes]

    default_repr = bi['repr']
    def patched_repr(obj):
        for patch in patches:
            if patch.recognise(obj):
                try:
                    return patch.repr(obj)
                except Exception as ex:   # pylint: disable=broad-except
                    print("Internal error: %s" % (ex,))

        # Fall back to the default
        return default_repr(obj)

    bi['repr'] = patched_repr


def disable_patch():
    global default_repr     # pylint: disable=global-statement

    if default_repr is None:
        raise RuntimeError('repr() patching is already disabled')

    bi['repr'] = default_repr
    default_repr = None
