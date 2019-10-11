from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib import admin
from django.forms.widgets import Textarea, TextInput
from adminsortable.admin import NonSortableParentAdmin, SortableTabularInline
from . import models
from django.db.models import TextField, CharField


class TextWidget(Textarea):
    def __init__(self, attrs=None):
        default_attrs = {'cols': '26', 'rows': '3'}
        if attrs:
            default_attrs.update(attrs)
        super(TextWidget, self).__init__(default_attrs)


class CharsWidget(TextInput):
    def __init__(self, attrs=None):
        default_attrs = {'size': '18'}
        if attrs:
            default_attrs.update(attrs)
        super(CharsWidget, self).__init__(default_attrs)


class InputSettingsFieldInline(SortableTabularInline):
    model = models.InputSettingsField
    fields = ('input_name', 'output_name', 'date_format', 'default_value',
        'exclude_if_empty', 'omit', 'example_value')
    formfield_overrides = {
        TextField: {'widget': TextWidget},
        CharField: {'widget': CharsWidget},
    }


class InputSettingsAdmin(NonSortableParentAdmin):
    list_display = ('name', 'default_format', 'uid')
    readonly_fields = ('uid',)
    fields = ('uid', 'name', 'description', 'default_format')
    inlines = [InputSettingsFieldInline]
    actions = ['update_field_definitions']

    def get_fields(self, request, obj=None):
        if obj is None:
            return ('name', 'description', 'default_format')
        return ('uid', 'name', 'description', 'default_format')

    def update_field_definitions(self, request, queryset):
        for settings in queryset:
            settings.update_field_definitions()
        self.message_user(request, ugettext("Updated field definitions"))
    update_field_definitions.short_description = _("Update field definitions")


class InputAdmin(admin.ModelAdmin):
    list_display = ('settings', 'format', 'internal_source', 'processed',
        'modified', 'raw_content')
    list_filter = ('format', 'internal_source', 'processed', 'created',
        'modified', 'settings')
    actions = ['update_field_definitions', 'notify_input']
    
    def get_fields(self, request, obj=None):
        if obj is None:
            return ('settings', 'format', 'processed', 'raw_content')
        return ('settings', 'internal_source', 'format', 'processed', 'raw_content',
            'created', 'modified', 'data')

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return []
        return self.get_fields(request, obj)

    def update_field_definitions(self, request, queryset):
        for settings in queryset:
            settings.update_field_definitions()
        self.message_user(request, ugettext("Updated field definitions"))
    update_field_definitions.short_description = _("Update field definitions")

    def data(self, obj=None):
        if obj is None:
            return None
        return obj.get_data()

    def notify_input(self, request, queryset):
        for input in queryset:
            input.notify()
        self.message_user(request, ugettext("Inputs notified."))
    notify_input.short_description = _("Notify inputs")


class WebhookAdmin(admin.ModelAdmin):
    list_display = ('uid', 'name', 'settings', 'url')
    fields = ('uid', 'name', 'description', 'settings', 'url')
    readonly_fields = ('uid', 'url')

    def url(self, obj=None):
        if obj is None:
            return None
        return obj.get_webhook_url()


admin.site.register(models.InputSettings, InputSettingsAdmin)
admin.site.register(models.Input, InputAdmin)
admin.site.register(models.Webhook, WebhookAdmin)
