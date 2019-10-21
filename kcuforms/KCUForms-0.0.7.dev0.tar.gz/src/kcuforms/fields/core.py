# -*- coding: utf-8 -*-

import sys
from abc import ABCMeta, abstractmethod
from datetime import datetime as dt, date

import re
from functools import partial

import six

from kcuforms.validators import date_type, list_type, dict_type, many_type

from kcuforms.utils import field_exception
from kcuforms.errors import FieldError

__all__ = (
    "BooleanField",
    "IPv4Field",
    "RangeField",
    "TimestampField",
    "DateField",
    "IntegerField",
    "ListField",
    "StringField",
    "DictField",
    "FloatField",
    "ListArrayField",
    "ListStrField"
)


class BaseField(object):
    __metaclass__ = ABCMeta

    __baseattrs__ = {
        'name': '_NAME',
        'required': '_REQUIRED',
        'type': '_TYPE',
        'default': '_DEFAULT',
        'action': '_ACTION',
        'location': '_LOCATION'
    }

    _NAME = None
    _REQUIRED = False
    _TYPE = None
    _DEFAULT = None
    _ACTION = None
    _LOCATION = None

    def __init__(self, *args, **kwargs):
        for key, default_name in self.__baseattrs__.items():
            setattr(self, key, kwargs.get(key, getattr(self, default_name, None)))

    @property
    def baseattrs(self):
        return self.__baseattrs__.keys()

    @abstractmethod
    def validate(self, val):
        pass


class StringField(BaseField):
    # if py2 _TYPE = unicode
    # if py3 _TYPE = str
    # 4 both None
    _TYPE = str
    _DEFAULT = u''
    _PATTERN = None

    def __init__(self, *args, **kwargs):
        super(StringField, self).__init__(*args, **kwargs)
        self.pattern = kwargs.get('pattern', self._PATTERN)

    @field_exception
    def validate(self, val):
        if self.pattern is not None and val is not None:
            if isinstance(val, six.string_types):
                if not re.match(self.pattern, val):
                    raise FieldError(u'{}: "{}" not match "{}"'.format(self.name, val, self.pattern))
            else:
                raise FieldError(u'{}: {} is not string type'.format(self.name or 'value', val))
        return val


class IPv4Field(StringField):
    _PATTERN = "^(((\\d{1,2})|(1\\d{2})|(2[0-4]\\d)|(25[0-5]))\\.){3}((\\d{1,2})|(1\\d{2})|(2[0-4]\\d)|(25[0-5]))$"
    _DEFAULT = None


class BooleanField(BaseField):
    _TYPE = bool
    _DEFAULT = False

    def __init__(self, *args, **kwargs):
        super(BooleanField, self).__init__(*args, **kwargs)

    @field_exception
    def validate(self, val):
        return self.type(val)


class IntegerField(BaseField):
    _TYPE = int
    _DEFAULT = -sys.maxsize
    _MIN = -sys.maxsize
    _MAX = sys.maxsize

    def __init__(self, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)
        self.min = kwargs.get('min', self._MIN)
        self.max = kwargs.get('max', self._MAX)

    @field_exception
    def validate(self, val):
        if val is not None:
            if val > self.max or val < self.min:
                raise FieldError(u'{}: {} not in [{}, {}]'.format(self.name, val, self.min, self.max))
        else:
            pass
        return val


class DateField(BaseField):
    _FORMAT = '%Y%m%d'
    _TYPE = partial(date_type, fmt=_FORMAT)
    _DEFAULT = date.today()

    def __init__(self, *args, **kwargs):
        super(DateField, self).__init__(*args, **kwargs)
        self.format = kwargs.get('format', self._FORMAT)
        self.type = partial(date_type, fmt=self.format)

    @field_exception
    def validate(self, val):
        if isinstance(val, (str, str)):
            self.type(val)
        return val


class TimestampField(BaseField):
    _TYPE = int
    _DEFAULT = 0
    _MIN = 0
    _MAX = sys.maxsize

    def __init__(self, *args, **kwargs):
        super(TimestampField, self).__init__(*args, **kwargs)
        self.min = kwargs.get('min', self._MIN)
        self.max = kwargs.get('max', self._MAX)

    @field_exception
    def validate(self, val):
        if val is not None:
            if val > self.max or val < self.min:
                raise FieldError(u'{}: {} not in [{}, {}]'.format(self.name, val, self.min, self.max))
        else:
            pass
        return dt.utcfromtimestamp(val / 1000.0)


class RangeField(BaseField):
    _LEFT = IntegerField()
    _RIGHT = IntegerField()
    _TYPE = str
    _OPERATOR = '[]'
    _DEFAULT = (_LEFT.default, _RIGHT.default, _OPERATOR)

    def __init__(self, *args, **kwargs):
        super(RangeField, self).__init__(*args, **kwargs)
        self.left = kwargs.get('left', self._LEFT)
        self.right = kwargs.get('right', self._RIGHT)
        self.operator = kwargs.get('operator', self._OPERATOR)
        self.default = kwargs.get('default', (self.left.default, self.right.default, self.operator))

    @field_exception
    def validate(self, val):
        val = val.split(',')
        left_val = self.left.validate(val[0])
        right_val = self.right.validate(val[1])
        if left_val > right_val:
            raise FieldError(u'{} > {}'.format(left_val, right_val))
        return (left_val, right_val), self.operator


class ManyField(BaseField):
    _TYPE = partial(many_type)
    _DEFAULT = ''
    _VALIDATOR = StringField()

    def __init__(self, *args, **kwargs):
        super(ManyField, self).__init__(*args, **kwargs)
        self.validator = kwargs.get('validator', self._VALIDATOR)
        self.default = kwargs.get('default', self._DEFAULT)
        self.type = kwargs.get('type', self._TYPE)

    @field_exception
    def validate(self, val):
        rets = []
        if isinstance(val, (str, str)):
            val = self.type(val)
        for v in val:
            rets.append(self.validator.validate(v))
        return rets


class ListStrField(BaseField):
    _TYPE = partial(list_type)
    _DEFAULT = []
    _MIN = 0
    _MAX = sys.maxsize
    _VALIDATOR = StringField()

    def __init__(self, *args, **kwargs):
        super(ListStrField, self).__init__(*args, **kwargs)
        self.validator = kwargs.get('validator', self._VALIDATOR)
        self.default = kwargs.get('default', self._DEFAULT)
        self.type = kwargs.get('type', self._TYPE)
        self.min = kwargs.get('min', self._MIN)
        self.max = kwargs.get('max', self._MAX)

    @field_exception
    def validate(self, val):
        ret = []
        val = self.type(val)
        for v in val:
            ret.append(self.validator.validate(v))
        if len(ret) > self.max or len(ret) < self.min:
            raise FieldError(u'{}: length {} not in [{}, {}]'.format(self.name, len(ret), self.min, self.max))
        return ret


ListField = ListStrField


class ListArrayField(ListField):
    _TYPE = str
    _ACTION = 'append'
    _DEFAULT = []
    _MIN = 0
    _MAX = sys.maxsize
    _VALIDATOR = StringField()

    def __init__(self):
        super(ListfArrayField, self).__init__(*args, **kwargs)

    @field_exception
    def validate(self, val):
        ret = []
        for v in val:
            ret.append(self.validator.validate(v))
        if len(ret) > self.max or len(ret) < self.min:
            raise ParamError(u'{}: length {} not in [{}, {}]'.format(self.name, len(ret), self.min, self.max))
        return ret


class DictField(BaseField):
    _TYPE = partial(dict_type)
    _DEFAULT = {}
    _VALIDATOR = StringField()
    _VALIDATORS = {}

    def __init__(self, *args, **kwargs):
        super(DictField, self).__init__(*args, **kwargs)
        self.validator = kwargs.get('validator', self._VALIDATOR)
        self.validators = kwargs.get('validators', self._VALIDATORS)
        self.default = kwargs.get('default', self._DEFAULT)
        self.type = kwargs.get('type', self._TYPE)

    @field_exception
    def validate(self, val):
        rets = {}
        val = self.type(val)
        for k, v in val.items():
            if self.validators and k not in self.validators:
                raise FieldError(u'{} is not in {}'.format(k, list(self.validators.keys())))
            else:
                rets[k] = self.validators.get(k, self.validator).validate(v)
        return rets


class FloatField(IntegerField):
    _TYPE = float
    _DEFAULT = 0.0
