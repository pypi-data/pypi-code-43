from django import template

register = template.Library()


@register.filter
def attr(value, attr_name):
    from redmin.utils import attr
    return attr(value, attr_name, default="")
