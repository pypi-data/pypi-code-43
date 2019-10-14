import json
from collections import OrderedDict

from django import forms
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import ChoiceField

from redmin.models import Permission, PermissionItem, Field, Filter
from redmin.utils import attr
from .mixins import ContextMixin, AccessMixin


class AdminFormView(SuccessMessageMixin, ContextMixin, AccessMixin):

    def get_form_class(self):
        user = self.request.user
        attributes = [field.attribute for field in Field.get_fields(user, self.model) if "." not in field.attribute and field.formable]
        form = type(f"DynamicForm_Model_{self.model.__name__}_User_{user.id}", (forms.ModelForm,), dict(
            Meta=type("Meta", (), dict(
                model=self.model,
                fields=attributes,
            )),
            __module__=__name__
        ))
        return form

    def post(self, request, *args, **kwargs):
        if Permission.has_permission(self.request.user, self.model, PermissionItem.savable):
            return super().post(request, *args, **kwargs)
        else:
            return self.handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model"] = self.model
        context["model_name"] = self.model.__name__
        group_fields = Field.get_group_fields(self.request.user, self.model, has_domain=True, reverse=False)
        context["group_fields_json"] = json.dumps([[{'attribute': field.attribute, "class": field.attribute_domain.get_model().__name__} for field in fields] for fields in group_fields])
        self.add_foreign_field_choices(context["form"], attr(context, "object"), group_fields)
        return context

    def get_option_query(self, cls):
        return cls.objects

    def add_foreign_field_choices(self, form, obj, group_fields):
        choices = []
        for foreign_fields in group_fields:
            last_field: Field = None
            last_value = None
            foreign_fields = [field for field in foreign_fields if field.formable]
            for index in range(len(foreign_fields)):
                field = foreign_fields[index]
                cls = field.model
                queryset = None
                attribute = field.attribute
                if index == 0 or last_value or last_field.nullable:
                    queryset = self.get_option_query(cls)
                    if last_value:
                        x = last_field.attribute[len(attribute) + 1:]
                        if x:
                            filters = {f"{x}_id": last_value}
                            queryset = queryset.filter(**filters)

                queryset = Filter.filter(queryset, self.request, cls)
                options = [(e.id, str(e)) for e in queryset.all()] if queryset else []
                if len(options) > 1:
                    options = [('', '------')] + options
                value = attr(obj, f'{attribute}_id')
                choices.append((attribute, ChoiceField(
                    required=True if form.fields.pop(attribute, False) else False,
                    initial=value,
                    label=field.title,
                    choices=options
                )))

                last_value = value
                last_field = field

        fields = OrderedDict(choices)
        fields.update(form.fields)
        form.fields = fields
