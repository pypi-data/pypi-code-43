import json

from django import template

register = template.Library()


@register.filter(name='jsonify')
def jsonify(data):
    if not data:
        return

    if isinstance(data, dict):
        return data
    else:
        return json.loads(data)
