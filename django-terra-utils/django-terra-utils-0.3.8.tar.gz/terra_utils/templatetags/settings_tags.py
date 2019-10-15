from django import template
from django.utils.html import mark_safe

from .. import settings as app_settings

register = template.Library()


@register.simple_tag
def front_url():
    return mark_safe(app_settings.FRONT_URL)


@register.simple_tag
def hostname():
    return mark_safe(app_settings.HOSTNAME)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
