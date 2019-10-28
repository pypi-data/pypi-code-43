import json
import re

from django.utils.safestring import SafeText

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


def get_field_label(obj, field):
    """
    Returns the label for a field based preferably based on obj's model.
    Falls back to replacing dashes and underscores with " ".
    :param obj: A model instance or a QuerySet.
    :param field: A string indicating the field to get the label for.
    :return:
    """
    try:
        model = get_model(obj)

        # If column key is "__str__", use model name as label.
        if field == '__str__':
            field = model.__name__

        # If model field can be found, use it's verbose name as label.
        else:
            field = model._meta.get_field(field)
            field = field.verbose_name

    # If label cannot be found, fall back to replacing dashes and underscores with " ".
    except:
        regex = re.compile('[_-]+')
        field = re.sub(regex, ' ', field)
    return field


def get_model(obj):
    """
    Tries to return a model based obj.
    :param obj: A model instance or a QuerySet.
    :return: The found model class or None.
    """
    try:
        return obj._meta.model
    except AttributeError:
        return obj.model
    except:
        return None


def merge_config(kwargs):
    """
    Merges "config" and other items in kwarg to generate configuration dict.
    Other kwargs override items in config.
    :param kwargs: (optional) dict in in kwargs mirroring other kwargs.
    :return: A merged dict containing configuration.
    """
    config = kwargs.pop('config', {})
    _kwargs = config.copy()
    _kwargs.update(kwargs)
    kwargs = _kwargs

    return kwargs


def parse_arg(arg, default=None):
    """
    Parses an argument (or value in kwargs)

    Syntax::

        Comma separated:
        - dict (Key value): "foo:bar,bar:baz" -> {'foo': 'bar', 'bar: 'baz')
        - list: "foo,bar,baz" -> ['foo, 'bar', baz']
        - string: "foo": "foo"

        JSON:
        - "[{"foo": "bar"}, {"bar": "baz"}]" -> [{'foo': 'bar'}, {'bar: 'baz')]

        Edge case:
        Given a dict as default ({}) list is converted into matching pair dict:
        - parse_arg("foo,bar,baz", {}) -> {'foo': 'foo', 'bar': 'bar', 'baz': 'baz}

        Given None returns default:
        - None -> default

        Given a non-string arg returns value directly.
        - True -> True

    :param arg: The input value to parse.
    :param default: Returned when arg is None.
    :return: The parsed arg.
    """
    if arg is None:
        return default

    if type(arg) != str and type(arg) != SafeText:
        return arg

    if ',' in arg or ':' in arg:
        try:
            return json.loads(arg)
        except JSONDecodeError:
            pass

        lst = [entry.strip() for entry in arg.strip().split(',') if entry]

        if ':' in arg or isinstance(default, dict):
            dct = {}
            for value in lst:
                try:
                    key, val = value.split(':')
                except ValueError:
                    key = value
                    val = value
                dct[key] = val or key
            return dct
        return lst
    return arg


def parse_kwarg(kwargs, name, default=None):
    """
    Parses value of name of kwargs.
    See parse_arg for syntax of value.

    :param kwargs:  Dict containing key name.
    :param name: The key in kwargs to parse.
    :param default: The default value if the kwargs[name] is None.
    :return: The parsed value of kwargs[name].
    """
    value = kwargs.get(name, default)
    return parse_arg(value, default)


def get_recursed_field_value(obj, field):
    """
    Finds a field value in an object by recursing through related fields.
    :param obj: A model instance.
    :param field: A field, possibly on a related instance. Example: "author__first_name".
    :return: The value of the final field.
    """
    fields = field.split('__')
    while len(fields) > 1:
        field = fields.pop(0)
        obj = getattr(obj, field)
    return getattr(obj, fields[0])
