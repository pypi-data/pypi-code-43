
import re

from django import forms
from django.contrib import admin

__all__ = ['FieldArrayTextFilter']


class FieldArrayTextFilter(admin.FieldListFilter):

    template = 'medicine_utils/admin/array_text_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '{}__in'.format(field_path)

        for p in self.expected_parameters():
            if p in params:
                value = params.pop(p)
                value = value.replace('\n', ',')
                value = re.sub('[^0-9,]', '', value)
                value = value.strip(',')
                value = ', '.join(list(filter(lambda v: v.isdigit(), [v for v in value.split(',')])))
                params[p] = value

        super().__init__(field, request, params, model, model_admin, field_path)

        self.form = self.get_form(request)

    def get_form(self, request):
        form_class = self._get_form_class()
        form_defaults = {
            self.lookup_kwarg: ','.join(self.used_parameters.get(self.lookup_kwarg, ''))
        }
        return form_class(form_defaults)

    def choices(self, cl):
        yield {
            'system_name': self.lookup_kwarg,
            'query_string': cl.get_query_string(
                {}, remove=self.lookup_kwarg
            )
        }

    def expected_parameters(self):
        return [self.lookup_kwarg]

    def _get_form_class(self):
        fields = {
            self.lookup_kwarg: forms.CharField(widget=forms.Textarea())
        }

        form_class = type(
            str('Form'),
            (forms.BaseForm,),
            {'base_fields': fields}
        )
        return form_class
