from django import template

register = template.Library()


def string(value):
    if value is None:
        return ""
    return f"{value}"


register.filter('string', string)
