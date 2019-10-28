import re

from rijkshuisstijl.templatetags.rijkshuisstijl import register


@register.filter
def input_date_format(value):
    """
    Tries to convert value to a valid <input type="date"> value.
    :param value: Can be either datetime or "dd-mm-yyyy" formatted string.
    :return: "yyyy-mm-dd" formatted string, compatible with <input type="date">.
    """
    if value:
        try:
            if hasattr(value, 'date'):
                return value.date().isoformat()
            if hasattr(value, 'isoformat'):
                return value.isoformat()

            regex = re.compile('(\d\d)-(\d\d)-(\d\d\d\d)')
            match = re.match(regex, value)

            if match:
                return '{}-{}-{}'.format(match[3], match[2], match[1])
            return value
        except AttributeError:
            return value


@register.filter
def input_time_format(value):
    """
    Tries to convert value to a valid <input type="time"> value.
    :param value: Can be either datetime or "hh:mm:ss" formatted string.
    :return: "hh:mm" formatted string, compatible with <input type="time">.
    """
    if value:
        try:
            if hasattr(value, 'time'):
                return value.time().isoformat()
            if hasattr(value, 'isoformat'):
                return value.isoformat()

            regex = re.compile('^(\d\d):(\d\d):(\d\d)$')
            match = re.match(regex, value)

            if match:
                return '{}:{}'.format(match[1], match[2])
            return value
        except AttributeError:
            return value


@register.filter
def get(value, key):
    """
    Gets a value from a dict by key.
    Returns empty string on failure.
    :param value: A dict containing key.
    :return: The key's value or ''.
    """
    try:
        return value.get(key, '')
    except:
        return ''


@register.filter
def get_attr_or_get(value, key):
    """
    Gets an attribute from an object or a value from a dict by key.
    Returns empty string on failure.
    :param value: An object or dict containing key.
    :return: The key's value or ''.
    """
    try:
        return getattr(value, key, '')
    except AttributeError:
        return get(value, key, '')
    except:
        return ''
