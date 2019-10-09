import re


from django.template.defaulttags import register


@register.filter
def add(value, arg):
    return value + arg


@register.filter
def input_date_format(value):
    if value:
        try:
            if value.date:
                return value.date().isoformat()

            regex = re.compile('(\d\d)-(\d\d)-(\d\d\d\d)')
            match = re.match(regex, value)

            if match:
                return '{}-{}-{}'.format(match[3], match[2], match[1])
            return value
        except AttributeError:
            return value


@register.filter
def input_time_format(value):
    if value:
        try:
            if value.date:
                return value.time().isoformat()

            regex = re.compile('^(\d\d):(\d\d):(\d\d)$')
            match = re.match(regex, value)

            if match:
                return '{}:{}'.format(match[1], match[2])
            return value
        except AttributeError:
            return value


@register.filter
def get(obj, key):
    try:
        return obj.get(key)
    except:
        return ''


@register.filter
def get_attr(obj, key):
    try:
        return getattr(obj, key)
    except AttributeError:
        return get(obj, key)
    except:
        return ''


@register.filter()
def make_object(value, key):
    class TemplateObject:
        pass

    obj = TemplateObject()
    setattr(obj, key, value)
    setattr(obj, 'name', 'foo')
    setattr(obj, 'auto_id', 'id')
    setattr(obj, 'css_classes', 'id')
    setattr(obj, 'errors', 'id')
    return obj
