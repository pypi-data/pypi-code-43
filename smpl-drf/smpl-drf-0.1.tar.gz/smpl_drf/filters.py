
import django_filters

from django import forms
from django.utils.translation import ugettext_lazy as _


class NullBooleanSelect(forms.Select):
    def __init__(self, attrs=None):
        choices = (
            ('false', _('No')),
            ('true', _('Yes')),
            ('', _('All')),
        )
        super().__init__(attrs, choices)

    def format_value(self, value):
        try:
            return {True: 'true', False: 'false'}[value]
        except KeyError:
            return ''

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        return {
            'true': True,
            True: True,
            'false': False,
            False: False,
        }.get(value)


class NullBooleanField(forms.NullBooleanField):
    widget = NullBooleanSelect


class NullBooleanFilter(django_filters.BooleanFilter):
    field_class = NullBooleanField
