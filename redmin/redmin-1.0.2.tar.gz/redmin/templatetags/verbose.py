from django import template

register = template.Library()


def verbose(value, attr_name):
    fields = value.__class__._meta.fields
    title = [f.title for f in fields if f.name == attr_name].pop()
    if title:
        return title
    else:
        return ""


register.filter('verbose', verbose)
