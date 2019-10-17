from django.forms import SelectMultiple, CheckboxSelectMultiple
from django.utils.text import format_lazy
from .views import ModelAdminAutocompleteJsonView
from django.contrib.admin import widgets
from django.contrib.admin.widgets import (AutocompleteSelect, AutocompleteSelectMultiple, )
from django.urls import reverse
from django.utils.translation import gettext as _


class AutocompleteSelectMixin:
    view_name = None

    def __init__(self, *args, **kwargs):
        view_name = kwargs.pop('view_name', None)
        super().__init__(*args, **kwargs)
        self.view_name = view_name

    def get_url(self):
        view_name = "{}:{}".format(self.admin_site.name, self.view_name)
        print("+++++++++++")
        print(view_name)
        print("+++++++++++")
        return reverse(view_name)


class SingleAutocompleteSelect(AutocompleteSelectMixin, AutocompleteSelect):
    pass


class MultipleAutocompleteSelect(AutocompleteSelectMixin, AutocompleteSelectMultiple):
    pass


class AutoCompleteModelMixin:
    autocomplete_fields = ()
    autocomplete_extra = {}

    def generate_view_name(self, field_name):
        """
        Generate view name for a field_name
        """
        app_name = self.model._meta.app_label.lower()
        model_name = self.model._meta.object_name.lower()
        related_model = getattr(self.model, field_name).field.remote_field.model
        related_model_name = related_model.__name__.lower()
        view_name = f"{app_name}_{model_name}_{related_model_name}_autocomplete"
        return view_name

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # If it uses an intermediary model that isn't auto created, don't show
        # a field in admin.
        if not db_field.remote_field.through._meta.auto_created:
            return None
        db = kwargs.get('using')
        if 'widget' not in kwargs:
            if db_field.name in self.get_autocomplete_fields(request):
                view_name = self.generate_view_name(db_field.name)
                kwargs['widget'] = MultipleAutocompleteSelect(db_field.remote_field, self.admin_site, view_name=view_name)
            elif db_field.name in self.raw_id_fields:
                kwargs['widget'] = widgets.ManyToManyRawIdWidget(db_field.remote_field, self.admin_site, using=db)
            elif db_field.name in [*self.filter_vertical, *self.filter_horizontal]:
                kwargs['widget'] = widgets.FilteredSelectMultiple(
                    db_field.verbose_name,
                    db_field.name in self.filter_vertical
                )

        if 'queryset' not in kwargs:
            queryset = self.get_field_queryset(db, db_field, request)
            if queryset is not None:
                kwargs['queryset'] = queryset

        form_field = db_field.formfield(**kwargs)
        if (isinstance(form_field.widget, SelectMultiple) and
                not isinstance(form_field.widget, (CheckboxSelectMultiple, AutocompleteSelectMultiple))):
            msg = _('Hold down "Control", or "Command" on a Mac, to select more than one.')
            help_text = form_field.help_text
            form_field.help_text = format_lazy('{} {}', help_text, msg) if help_text else msg
        return form_field

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Get a form Field for a ForeignKey.
        """
        if 'widget' not in kwargs:
            if db_field.name in self.get_autocomplete_fields(request):
                view_name = self.generate_view_name(db_field.name)
                kwargs['widget'] = SingleAutocompleteSelect(db_field.remote_field, self.admin_site, view_name=view_name)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def check_autocomplete_extra(self):
        """
        Validation of auto_complete fields
        """
        for field in self.autocomplete_extra.keys():
            if field not in self.autocomplete_fields:
                raise ValueError(f"'{field}' must be included in 'autocomplete_fields'")

    def get_autocomplete_field_settings(self):
        autocomplete_field_settings = {
            field: {"lookup_field": self.autocomplete_extra.get(field, {}).get("lookup_field", "id")} for field
            in self.get_autocomplete_fields(request=None)}
        return autocomplete_field_settings

    def get_urls(self):
        """
        Generating new urls that are used to get the autocomplete results
        """
        from django.urls import path
        auto_complete_urls = []
        urls = super().get_urls()
        self.check_autocomplete_extra()
        autocomplete_field_settings = self.get_autocomplete_field_settings()
        app_name = self.model._meta.app_label.lower()
        model_name = self.model._meta.object_name.lower()
        for field_name, field_settings in autocomplete_field_settings.items():
            related_model = getattr(self.model, field_name).field.remote_field.model
            related_model_name = related_model.__name__.lower()
            view_name = f"{app_name}_{model_name}_{related_model_name}_autocomplete"
            url_path = f"{app_name}-{model_name}-{related_model_name}-autocomplete/"
            view_kwargs = {
                "model_admin": self,
                "autocomplete_model": related_model,
                "lookup_field": field_settings["lookup_field"]
            }
            auto_complete_urls.append(
                path(url_path, ModelAdminAutocompleteJsonView.as_view(**view_kwargs), name=view_name)
            )
        return auto_complete_urls + urls
