from django.shortcuts import redirect
from django.contrib import admin, messages
from django.utils.translation import ugettext_lazy as _, ugettext
try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse
from oauth_clients import models as client_models
from . import models
from . import forms
from . import tasks


class SettingsAdmin(admin.ModelAdmin):
    list_display = ('oauth_client',)

    def has_add_permission(self, request):
        if models.Settings.objects.count() != 0:
            return False
        return super(SettingsAdmin, self).has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'simplified_scope')
    fields = ('user_id', 'username', 'simplified_scope')
    readonly_fields = fields

    def simplified_scope(self, obj):
        return obj.get_scope()
    simplified_scope.short_description = _("Scope")

    def add_view(self, request, *args, **kwargs):
        info = self.model._meta.app_label, self.model._meta.model_name
        redirect_info = client_models.Client._meta.app_label, client_models.Client._meta.model_name
        view_name = 'admin:{}_{}_changelist'.format(*info)
        settings = models.Settings.objects.first()
        if settings is None or settings.oauth_client is None:
            message = ugettext("Oauth client not configured.")
            self.message_user(request, message, messages.WARNING)
            return redirect(view_name)
        redirect_url = settings.oauth_client.complete_authorization_url(request)
        final_redirection = request.build_absolute_uri(reverse(view_name))
        authorization_url = settings.oauth_client.start_authorization_url(
            request, redirect_url, final_redirection)
        return redirect(authorization_url)


class SpreadsheetAdmin(admin.ModelAdmin):
    list_display = ('name', 'spreadsheet_name', 'sheet_name',
        'last_imported_row', 'last_imported_date', 'enabled')
    list_filter = ['enabled']
    actions = ['import_spreadsheets', 'reset_importing']
    
    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = forms.SpreadSheetForm
        return super(SpreadsheetAdmin, self).get_form(request, obj, **kwargs)

    def get_fields(self, request, obj=None):
        if obj is None:
            return super(SpreadsheetAdmin, self).get_fields(request, obj)
        return ('access_token', 'url', 'name', 'spreadsheet_name', 'uid', 'sheet_index',
            'sheet_name', 'omit_first_row', 'last_imported_row', 'last_imported_date',
            'input_settings', 'enabled')

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return super(SpreadsheetAdmin, self).get_readonly_fields(request, obj)
        return ('spreadsheet_name', 'uid', 'sheet_name', 'last_imported_row', 'last_imported_date')

    def import_spreadsheets(self, request, queryset):
        for spreadsheet in queryset:
            tasks.import_google_spreadsheet.delay(spreadsheet.pk)
        self.message_user(request, ugettext("The selected spreadsheets are being imported."),
            messages.INFO)
    import_spreadsheets.short_description = _("Import spreadsheets")

    def reset_importing(self, request, queryset):
        for spreadsheet in queryset:
            spreadsheet.reset_importing()
        self.message_user(request, ugettext("Reseted import of selected spreadsheets."))
    reset_importing.short_description = _("Reset importing")

admin.site.register(models.Settings, SettingsAdmin)
admin.site.register(models.AccessToken, AccessTokenAdmin)
admin.site.register(models.Spreadsheet, SpreadsheetAdmin)
