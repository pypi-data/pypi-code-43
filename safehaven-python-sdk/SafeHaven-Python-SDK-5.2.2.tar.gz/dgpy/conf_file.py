#
# Classes representing key/value configuration dictionaries and files.
#
import re
import os
import sys
import pwd
import copy
import types
import logging
import UserDict
import itertools

from types       import ListType, DictType
from collections import OrderedDict, Iterable
from dgpy.utils  import parse_key_value_from_fo

class ConfigDict(UserDict.DictMixin):
    """Dictionary variant for classes based on key/value items, with following additional features:
    1. allow both access object[key] and object.key
    2. if the optional %ATTR_MAP and %OPTIONAL_ATTR are present, perform validation:
      - ATTR_MAP maps <key> -> func(string) for each permitted key.
      - OPTIONAL_ATTR is a set of optional keys. If present, it must be a subset of ATTR_MAP.keys()
    """
    def __init__(self, config, allow_whitespace=False):
        """Initialize self from @config.
        @config:           key/value representation, one of
                           a) dictionary type ('dict' or 'OrderedDict') or
                           b) list of (key, value) pairs
                           c) iterable producing a list of type (b)
        @allow_whitespace: allow values to have trailing/leading whitespace
        """
        if hasattr(self, 'ATTR_MAP'):
            if not isinstance(config, dict):
                config = dict(config)

            have         = set(config.keys())
            may_have     = set(self.ATTR_MAP.keys())
            unknown_keys = have - may_have
            if unknown_keys:
                raise KeyError("unsupported %s configuration key(s): %s" % (self.__class__.__name__,
                                                                            ', '.join(map(repr, unknown_keys))))

            if hasattr(self, 'OPTIONAL_ATTR'):
                if not self.OPTIONAL_ATTR.issubset(may_have):
                    raise KeyError("Invalid OPTIONAL_ATTR %s" % ', '.join(self.OPTIONAL_ATTR - may_have))

                missing_keys = may_have - self.OPTIONAL_ATTR - have
                if missing_keys:
                    raise KeyError("missing %s configuration key(s): %s" % (self.__class__.__name__,
                                                                            ', '.join(map(repr, missing_keys))))

            # Order of %ATTR_MAP overrides the order in @config
            init_items = [(k, config[k]) for k in self.ATTR_MAP.keys() if k in config]
            for k,v in init_items:
                if v and not self.ATTR_MAP[k](v): # Empty values are O.K.
                    raise ValueError("invalid entry '%s = %r" % (k, v))

        elif type(config) is DictType:
            init_items = [(k, config[k]) for k in sorted(config.keys())]
        else:
            init_items = config

        self.__dict = OrderedDict(init_items)

        if not allow_whitespace:
            for k,v in self.__dict.iteritems():
                if re.search('(^\s+|\s+$)', v):
                    raise ValueError("whitespace in configuration: %s = %r" % (k, v))

    def __hash__(self):
        """Hash value is the ordered representation of wrapped key/value pairs.
        This implementation ignores additional attributes added in subclasses, i.e.
        subclasses must override this function if items are to be added to sets, dictionaries etc.
        """
        return hash(repr(self.__dict))

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.__cmp__(other) == 0

    def __ne__(self, other):
        return not self.__eq__(other)

    def __cmp__(self, other):
        """Compare configurations based on their hash values."""
        return hash(self) - hash(other)

    def __getattr__(self, name):
        if name in self.__dict:               # Allow access as self.<name>
            return self.__dict[name]
        return getattr(self.__dict, name)     # Fallback: delegate to wrapped dictionary (superclass)

    def __str__(self):
        """Print dictionary items first, then any additional attributes."""
        return "%s(%s)" % (self.__class__.__name__,  ', '.join('%s=%r' % e for e in itertools.chain(
            self.__dict.iteritems(),
            ((f, getattr(self, f)) for f in self.__dict__  if not f.endswith('__dict'))
        )))


class ConfFile(ConfigDict):
    """Utility class for key/value-based configuration files.
    Initializes from key/value file or from @keyvals dictionary.
    """
    def __init__(self, path, *keyvals):
        """
        @path:    full/absolute path of configuration file
        @keyvals: initial (key, val) pairs for this file
        """
        if keyvals:
            d = OrderedDict(keyvals)
        elif os.path.exists(path):
            d = parse_key_value_from_fo(open(path))
        else:
            d = {}

        # Handle shell variable references using '$var'.
        for k,v in d.iteritems():
            m = re.match('\s*\$(\S+)', v)
            if m:
                ref = m.group(1)
                if ref in d:
                    d[k] = d[ref]
                else:
                    raise SyntaxError("Mismatched reference %s=%s in %s" % (k, v, path))

        ConfigDict.__init__(self, d)
        self.path = path

def SyntropyValue(v):
    """Utility method to sanitize values into Syntropy strings."""
    if type(v) is types.NoneType:
        return "<none>"
    if type(v) is types.BooleanType:
        return str(v).lower()
    if type(v) in(types.IntType, types.FloatType, types.LongType):
        return str(v)
    return v

if __name__ == '__main__':
    pass
