from django import template

register = template.Library()


@register.filter
def display(obj, attr_name):
    from redmin.utils import display
    return display(obj, attr_name)
