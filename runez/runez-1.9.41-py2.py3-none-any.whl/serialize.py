"""
Convenience methods for (de)serializing objects
"""

import collections
import datetime
import io
import json
import logging
import os
from copy import copy

import runez.schema
from runez.base import decode, string_type, UNSET
from runez.convert import resolved_path, short, shortened
from runez.path import ensure_folder
from runez.system import abort, is_dryrun


LOG = logging.getLogger(__name__)
Serializable = None  # type: type # Set to runez.Serializable class once parsing of runez.serialize.py is past that class definition


def with_behavior(strict=UNSET, extras=UNSET, hook=UNSET):
    """
    Args:
        strict (bool | Exception | callable): False: don't perform any schema validation
                                              True: raise ValidationException when schema is not respected
                                              Exception: raise given exception when schema is not respected
                                              callable: call callable(reason) when schema is not respected

        extras (bool | Exception | callable | (callable, list)):
            False: don't do anything when there are extra fields in deserialized data
            True: call LOG.debug(reason) to report extra (not in schema) fields seen in data
            Exception: raise given Exception(reason) when extra fields are seen in data
            callable: call callable(reason) when extra fields are seen in data
            (callable, list): call callable(reason), except for extras mentioned in list

        hook (callable): If provided, call callable(meta: ClassMetaDescription) at the end of ClassMetaDescription initialization

    Returns:
        (type): Internal temp class (compatible with `Serializable` metaclass) indicating how to handle Serializable type checking
    """
    return BaseMetaInjector("_MBehavior", tuple(), {"behavior": DefaultBehavior(strict=strict, extras=extras, hook=hook)})


def is_serializable_descendant(base):
    """
    Args:
        base (type): Base class to examine

    Returns:
        (bool): True if `base` is a descendant of `Serializable` (but not `Serializable` itself)
    """
    return Serializable is not None and base is not Serializable and issubclass(base, Serializable)


def set_default_behavior(strict=UNSET, extras=UNSET):
    """
    Use this to change defaults globally at the start of your app (or in your conftest), for example:
        runez.serializable.set_default_behavior(strict=True)

    Args:
        strict (bool | Exception | callable): False: don't perform any schema validation
                                              True: raise ValidationException when schema is not respected
                                              Exception: raise given exception when schema is not respected
                                              callable: call callable(reason) when schema is not respected

        extras (bool | Exception | callable): False: don't do anything when there are extra fields in deserialized data
                                              True: call LOG.debug(reason) to report extra (not in schema) fields seen in data
                                              Exception: raise given Exception(reason) when extra fields are seen in data
                                              callable: call callable(reason) when extra fields are seen in data
    """
    if strict is not UNSET:
        DefaultBehavior.strict = strict

    if extras is not UNSET:
        DefaultBehavior.extras = extras


class DefaultBehavior(object):
    """
    Defines how to handle type mismatches and extra data in `Serializable`.
    Default behavior will be used only if no specific with_behavior() is used in Serializable descendant definition.

    Also carries an optional `hook` to call at the end of each Serializable descendant registration
    (global default for that does not make sense).
    """
    strict = False  # type: callable # Original default: don't strictly enforce type compatibility
    extras = False  # type: callable  # Original default: don't report extra fields seen in deserialized data (ie: ignore them)

    def __init__(self, strict=UNSET, extras=UNSET, hook=UNSET):
        """
        Args:
            strict (bool | callable): False: don't check, True: raise ValidationException on type mismatch, Exception: raise given exception
            extras (bool | callable | (callable, list)): See `with_behavior()`
            hook (callable): Called if provided at the end of ClassMetaDescription initialization
        """
        if strict is UNSET:
            strict = self.strict

        if extras is UNSET:
            extras = self.extras

        self.strict = self.to_callable(strict, runez.schema.ValidationException)
        self.hook = self.to_callable(hook, None)  # type: callable # Called if provided at the end of ClassMetaDescription initialization
        self.ignored_extras = None  # Internal, populated if given `extras` is a `tuple(callable, list)`

        if isinstance(extras, tuple) and len(extras) == 2:
            extras, self.ignored_extras = extras
            if hasattr(self.ignored_extras, "split"):
                self.ignored_extras = self.ignored_extras.split()

        else:
            self.ignored_extras = None

        self.extras = self.to_callable(extras, LOG.debug)

    def __repr__(self):
        result = []
        if self.strict:
            result.append("strict: %s" % shortened(self.strict))

        if self.extras:
            result.append("extras: %s" % shortened(self.extras))

        if self.ignored_extras:
            result.append("ignored extras: %s" % shortened(self.ignored_extras))

        if self.hook:
            result.append("hook: %s" % shortened(self.hook))

        if result:
            return ", ".join(result)

        return "lenient"

    @staticmethod
    def get_behavior(bases):
        """Determine behavior from given `bases` (base classes)"""
        strict = hook = UNSET
        for base in reversed(bases):
            meta = getattr(base, "_meta", None)
            if isinstance(meta, ClassMetaDescription) and meta.behavior is not None and is_serializable_descendant(base):
                # Let `strict` and `hook` be inherited from parent classes (but not `Serializable` itself)
                strict = meta.behavior.strict
                hook = meta.behavior.hook

        return DefaultBehavior(strict=strict, hook=hook)

    @staticmethod
    def to_callable(value, default):
        if not value:
            return None

        if callable(value):
            return value

        return default

    def handle_mismatch(self, class_name, field_name, problem, source):
        if self.strict:
            msg = " from %s" % source if source else ""
            msg = "Can't deserialize %s.%s%s: %s" % (class_name, field_name, msg, problem)
            if isinstance(self.strict, type) and issubclass(self.strict, Exception):
                raise self.strict(msg)

            self.strict(msg)

    def do_notify(self, message):
        if self.extras:
            if isinstance(self.extras, type) and issubclass(self.extras, Exception):
                raise self.extras(message)

            self.extras(message)

    def handle_extra(self, class_name, field_name):
        self.do_notify("'%s' is not an attribute of %s" % (field_name, class_name))

    def handle_extras(self, class_name, extras):
        if self.extras:
            if self.ignored_extras:
                for x in self.ignored_extras:
                    extras.pop(x, None)

            if extras:
                # We have more stuff in `data` than described in corresponding `._meta`
                self.do_notify("Extra content given for %s: %s" % (class_name, ", ".join(sorted(extras))))


def json_sanitized(value, stringify=decode, dt=str, keep_none=False):
    """
    Args:
        value: Value to sanitize
        stringify (callable | None): Function to use to stringify non-builtin types
        dt (callable | None): Function to use to stringify dates
        keep_none (bool): If False, don't include None values

    Returns:
        An object that should be json serializable
    """
    if value is None or isinstance(value, (int, float, string_type)):
        return value

    if hasattr(value, "to_dict"):
        value = value.to_dict()

    elif isinstance(value, set):
        value = sorted(value)

    if isinstance(value, (tuple, list)):
        return [json_sanitized(v, stringify=stringify, dt=dt, keep_none=keep_none) for v in value if keep_none or v is not None]

    if isinstance(value, dict):
        return dict(
            (
                json_sanitized(k, stringify=stringify, dt=dt, keep_none=keep_none),
                json_sanitized(v, stringify=stringify, dt=dt, keep_none=keep_none),
            )
            for k, v in value.items()
            if keep_none or v is not None
        )

    if isinstance(value, datetime.date):
        if dt is None:
            return value

        return dt(value)

    if stringify is None:
        return value

    return stringify(value)


def same_type(t1, t2):
    """
    :return bool: True if 't1' and 't2' are of equivalent types
    """
    if t1 is None or t2 is None:
        return t1 is t2

    if not isinstance(t1, type):
        t1 = t1.__class__

    if not isinstance(t2, type):
        t2 = t2.__class__

    if issubclass(t1, string_type) and issubclass(t2, string_type):
        return True

    return t1 == t2


def type_name(value):
    """
    Args:
        value: Some object, class, or None

    Returns:
        (str): Class name implementing 'value'
    """
    if value is None:
        return "None"

    if isinstance(value, string_type):
        return "str"

    if isinstance(value, type):
        return value.__name__

    return value.__class__.__name__


def applicable_bases(cls):
    yield cls
    for base in cls.__bases__:
        if is_serializable_descendant(base):
            yield base


def scan_attributes(cls):
    for key, value in cls.__dict__.items():
        if not key.startswith("_"):
            yield key, value


def scan_all_attributes(cls):
    seen = set()
    for base in applicable_bases(cls):
        for key, value in scan_attributes(base):
            if key not in seen:
                seen.add(key)
                yield key, value


class ClassMetaDescription(object):
    """Info on class attributes and properties"""

    def __init__(self, cls, mbehavior):
        self.name = type_name(cls)
        self.cls = cls
        self.attributes = {}
        self.properties = []
        self.behavior = mbehavior.behavior if mbehavior is not None else DefaultBehavior.get_behavior(cls.__bases__)

        by_type = collections.defaultdict(list)
        for key, value in scan_all_attributes(cls):
            if not key.startswith("_"):
                if value is not None and "property" in value.__class__.__name__:
                    self.properties.append(key)
                    continue

                descriptor = runez.schema.get_descriptor(value, required=False)
                if descriptor is not None:
                    self.attributes[key] = descriptor
                    by_type[descriptor.name].append(key)

        self.by_type = dict((k, sorted(v)) for k, v in by_type.items())  # Sorted to make testing py2/py3 deterministic
        if self.behavior.hook:
            self.behavior.hook(self)

    def __repr__(self):
        return "%s (%s attributes, %s properties)" % (type_name(self.cls), len(self.attributes), len(self.properties))

    def from_dict(self, data, source=None):
        """
        Args:
            data (dict): Raw data, coming for example from a json file
            source (str | None): Optional, description of source where 'data' came from

        Returns:
            (cls): Deserialized object
        """
        result = self.cls()
        # Call objects' own set_from_dict() to allow descendants to fine-tune its behavior if needed
        result.set_from_dict(data, source=source)
        return result

    def set_from_dict(self, obj, data, source=None):
        """
        Args:
            obj (Serializable): Object to populate
            data (dict): Raw data, coming for example from a json file
            source (str | None): Optional, description of source where 'data' came from
        """
        if data is None:
            given = {}

        else:
            given = data.copy()

        for name, descriptor in self.attributes.items():
            value = given.pop(name, descriptor.default)
            problem = descriptor.problem(value)
            if problem is None:
                value = descriptor.converted(value)

            else:
                self.behavior.handle_mismatch(self.name, name, problem, source)

            if value is None:
                setattr(obj, name, None)

            else:
                setter = getattr(obj, "set_%s" % name, None)
                if setter is None:
                    setattr(obj, name, value)

                else:
                    setter(value)

        self.behavior.handle_extras(self.name, given)

    def problem(self, value):
        """
        Args:
            value: Value to verify compliance of

        Returns:
            (str | None): Explanation of compliance issue, if there is any
        """
        for name, descriptor in self.attributes.items():
            problem = descriptor.problem(value.get(name))
            if problem is not None:
                return problem

        if self.behavior.extras:
            for key in value:
                if key not in self.attributes:
                    self.behavior.handle_extra(self.name, key)

    def changed_attributes(self, obj1, obj2):
        """
        Args:
            obj1 (Serializable): First object to inspect
            obj2 (Serializable): 2nd object to inspect

        Returns:
            (list): Tuple of attribute names and values for which values differ between `obj1` and `obj2`
        """
        assert obj1._meta is self and obj2._meta is self
        result = []
        for key in self.attributes:
            v1 = getattr(obj1, key)
            v2 = getattr(obj2, key)
            if v1 != v2:
                result.append((key, v1, v2))

        return sorted(result)


class BaseMetaInjector(type):
    """Used solely to provide common ancestor for `MetaInjector` and internal types returned by `with_behavior`"""


def add_metaclass(metaclass):
    """Class decorator for creating a class with a metaclass (taken from https://pypi.org/project/six/)."""
    def wrapper(cls):
        orig_vars = cls.__dict__.copy()
        slots = orig_vars.get("__slots__")
        if slots is not None:
            if isinstance(slots, str):
                slots = [slots]
            for slots_var in slots:
                orig_vars.pop(slots_var)
        orig_vars.pop("__dict__", None)
        orig_vars.pop("__weakref__", None)
        if hasattr(cls, "__qualname__"):
            orig_vars["__qualname__"] = cls.__qualname__
        return metaclass(cls.__name__, cls.__bases__, orig_vars)
    return wrapper


def filtered_bases(bases):
    fb = []
    mbehavior = None
    for base in bases:
        if base.__name__ == "_MBehavior":
            mbehavior = base

        else:
            fb.append(base)

    if mbehavior is None:
        return None, bases

    return mbehavior, tuple(fb)


def add_meta(meta_type):
    """A simplified metaclass that simply injects a `._meta` field of given type `meta_type`"""
    class MetaInjector(BaseMetaInjector):
        def __new__(cls, name, bases, dct):
            _, fb = filtered_bases(bases)
            return super(MetaInjector, cls).__new__(cls, name, fb, dct)

        def __init__(cls, name, bases, dct):
            mbehavior, fb = filtered_bases(bases)
            super(MetaInjector, cls).__init__(name, fb, dct)
            cls._meta = meta_type(cls, mbehavior)

    return add_metaclass(MetaInjector)


@add_meta(ClassMetaDescription)
class Serializable(object):
    """Serializable object"""

    _meta = None  # type: ClassMetaDescription  # This describes fields and properties of descendant classes, populated via metaclass

    def __new__(cls, *args, **kwargs):
        """Args passed to __new__() is deprecated in py3"""
        obj = super(Serializable, cls).__new__(cls)
        obj.reset()
        return obj

    def __eq__(self, other):
        if other is not None and other.__class__ is self.__class__:
            for name in self._meta.attributes:
                if not hasattr(other, name) or getattr(self, name) != getattr(other, name):
                    return False

            return True

    def __ne__(self, other):
        return not (self == other)

    def __copy__(self):
        return self.__class__.from_dict(self.to_dict())

    @classmethod
    def copy_of(cls, obj):
        """
        Args:
            obj (self.__class__ | None): Object to copy

        Returns:
            (self.__class__): Copy of `obj`, or brand new object if it was None
        """
        if obj is None:
            return cls()

        return obj.__copy__()

    def copy(self):
        """
        Returns:
            (self.__class__): Copy of this object
        """
        return copy(self)

    @classmethod
    def from_json(cls, path, default=None, fatal=True, logger=None):
        """
        Args:
            path (str): Path to json file
            default (dict | None): Default if file is not present, or if it's not json
            fatal (bool | None): Abort execution on failure if True
            logger (callable | None): Logger to use

        Returns:
            (cls): Deserialized object
        """
        result = cls()
        data = read_json(path, default=default, fatal=fatal, logger=logger)
        result.set_from_dict(data, source=short(path))
        return result

    @classmethod
    def from_dict(cls, data, source=None):
        """
        Args:
            data (dict): Raw data, coming for example from a json file
            source (str | None): Optional, description of source where 'data' came from

        Returns:
            (cls): Deserialized object
        """
        return cls._meta.from_dict(data, source=source)

    def set_from_dict(self, data, source=None, merge=False):
        """
        Args:
            data (dict): Raw data, coming for example from a json file
            source (str | None): Optional, description of source where 'data' came from
            merge (bool): If True, add `data` to existing fields
        """
        if merge:
            merged = self.to_dict()
            merged.update(data)
            data = merged

        self._meta.set_from_dict(self, data, source=source)

    def reset(self):
        """
        Reset all fields of this object to class defaults
        """
        for name, descriptor in self._meta.attributes.items():
            setattr(self, name, descriptor.default)

    def to_dict(self, stringify=decode, dt=str, keep_none=False):
        """
        Args:
            stringify (callable | None): Function to use to stringify non-builtin types
            dt (callable | None): Function to use to stringify dates
            keep_none (bool): If False, don't include None values

        Returns:
            (dict): This object serialized to a dict
        """
        raw = dict((name, getattr(self, name)) for name in self._meta.attributes)
        return json_sanitized(raw, stringify=stringify, dt=dt, keep_none=keep_none)


runez.schema.Serializable = Serializable


def read_json(path, default=None, fatal=True, logger=None):
    """
    Args:
        path (str | None): Path to file to deserialize
        default (dict | list | str | None): Default if file is not present, or if it's not json
        fatal (bool | None): Abort execution on failure if True
        logger (callable | None): Logger to use

    Returns:
        (dict | list | str): Deserialized data from file
    """
    path = resolved_path(path)
    if not path or not os.path.exists(path):
        if default is None:
            return abort("No file %s", short(path), fatal=(fatal, default))
        return default

    try:
        with io.open(path, "rt") as fh:
            data = json.load(fh)
            if default is not None and type(data) != type(default):
                return abort("Wrong type %s for %s, expecting %s", type(data), short(path), type(default), fatal=(fatal, default))

            if logger:
                logger("Read %s", short(path))

            return data

    except Exception as e:
        return abort("Couldn't read %s: %s", short(path), e, fatal=(fatal, default))


def represented_json(data, sort_keys=True, indent=2, keep_none=False, **kwargs):
    """
    Args:
        data (object | None): Data to serialize
        sort_keys (bool): Whether keys should be sorted
        indent (int | None): Indentation to use, if None: use compact (one line) mode
        keep_none (bool): If False, don't include None values
        **kwargs: Passed through to `json.dumps()`

    Returns:
        (dict | list | str): Serialized `data`, with defaults that are usually desirable for a nice and clean looking json
    """
    data = json_sanitized(data, keep_none=keep_none)
    if indent is None:
        kwargs.setdefault("separators", (", ", ": "))

    else:
        kwargs.setdefault("separators", (",", ": "))

    rep = json.dumps(data, sort_keys=sort_keys, indent=indent, **kwargs)
    if indent is None:
        return rep

    return "%s\n" % rep


def save_json(data, path, fatal=True, logger=None, sort_keys=True, indent=2, keep_none=False, **kwargs):
    """
    Args:
        data (object | None): Data to serialize and save
        path (str | None): Path to file where to save
        fatal (bool | None): Abort execution on failure if True
        logger (callable | None): Logger to use
        sort_keys (bool): Save json with sorted keys
        indent (int | None): Indentation to use
        keep_none (bool): If False, don't include None values
        **kwargs: Passed through to `json.dump()`

    Returns:
        (int): 1 if saved, -1 if failed (when `fatal` is False)
    """
    if data is None or not path:
        return abort("No file %s", short(path), fatal=fatal)

    try:
        path = resolved_path(path)
        ensure_folder(path, fatal=fatal, logger=None)
        if is_dryrun():
            LOG.info("Would save %s", short(path))
            return 1

        data = json_sanitized(data, keep_none=keep_none)
        if indent:
            kwargs.setdefault("separators", (",", ": "))

        with open(path, "wt") as fh:
            json.dump(data, fh, sort_keys=sort_keys, indent=indent, **kwargs)
            fh.write("\n")

        if logger:
            logger("Saved %s", short(path))

        return 1

    except Exception as e:
        return abort("Couldn't save %s: %s", short(path), e, fatal=(fatal, -1))
