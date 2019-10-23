from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.contenttypes.models import ContentType
from django.template.response import TemplateResponse
from django.urls import path

try: # Django 2.0
    from django.urls import reverse
except: # Django < 2.0
    from django.core.urlresolvers import reverse

from django.utils.safestring import mark_safe
from . import settings
from .models import CRUDEvent, LoginEvent, RequestEvent
from .admin_helpers import prettify_json, EasyAuditModelAdmin
from .settings import CRUD_EVENT_LIST_FILTER, LOGIN_EVENT_LIST_FILTER, REQUEST_EVENT_LIST_FILTER


# CRUD events
class CRUDEventAdmin(EasyAuditModelAdmin):
    list_display = ['get_event_type_display', 'content_type', 'object_id', 'object_repr_link', 'user_link', 'datetime']
    date_hierarchy = 'datetime'
    list_filter = CRUD_EVENT_LIST_FILTER
    search_fields = ['=object_id', ]
    readonly_fields = ['event_type', 'object_id', 'content_type',
                       'object_repr', 'user',
                       'user_pk_as_string', 'datetime', 'changed_fields_prettified', 'change_reason']
    exclude = ['changed_fields']

    def object_repr_link(self, obj):
        if obj.event_type == CRUDEvent.DELETE:
            html = obj.object_repr
        else:
            try:
                url = reverse("admin:%s_%s_change" % (
                    obj.content_type.app_label,
                    obj.content_type.model,
                ), args=(obj.object_id,))
                html = '<a href="%s">%s</a>' % (url, obj.object_repr)
            except:
                html = obj.object_repr
        return mark_safe(html)

    object_repr_link.short_description = 'object repr'

    def changed_fields_prettified(self, obj):
        return prettify_json(obj.changed_fields)

    changed_fields_prettified.short_description = 'changed fields'


if settings.ADMIN_SHOW_MODEL_EVENTS:
    admin.site.register(CRUDEvent, CRUDEventAdmin)


# Login events
class LoginEventAdmin(EasyAuditModelAdmin):
    list_display = ['datetime', 'get_login_type_display', 'user_link', 'username', 'remote_ip']
    date_hierarchy = 'datetime'
    list_filter = LOGIN_EVENT_LIST_FILTER
    search_fields = ['=remote_ip', 'username', ]
    readonly_fields = ['login_type', 'username', 'user', 'remote_ip', 'datetime', ]


if settings.ADMIN_SHOW_AUTH_EVENTS:
    admin.site.register(LoginEvent, LoginEventAdmin)


# Request events
class RequestEventAdmin(EasyAuditModelAdmin):
    list_display = ['datetime', 'user_link', 'method', 'url', 'remote_ip']
    date_hierarchy = 'datetime'
    list_filter = REQUEST_EVENT_LIST_FILTER
    search_fields = ['=remote_ip', 'username', 'url', 'query_string', ]
    readonly_fields = ['url', 'method', 'query_string', 'user', 'remote_ip', 'datetime', ]


if settings.ADMIN_SHOW_REQUEST_EVENTS:
    admin.site.register(RequestEvent, RequestEventAdmin)


class ModelAdminWithHistory(ModelAdmin):
    change_form_template = 'admin/easyaudit/change_form_with_history_button.html'

    def get_urls(self):
        return [
            path(
                '<path:object_id>/history/',
                self.admin_site.admin_view(self.changes_history),
                name=f'{self.model._meta.app_label}_{self.model._meta.model_name}_changes_history',
            ),
        ] + super().get_urls()

    def changes_history(self, request, object_id):
        original = self.get_object(request, object_id)

        if hasattr(original, 'history'):
            history = original.history
        else:
            history = CRUDEvent.objects.filter(
                content_type=ContentType.objects.get_for_model(original), object_id=original.id
            )

        context = {
            'opts': self.model._meta,
            'original': original,
            'history': history,
            **self.admin_site.each_context(request),
        }
        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            'admin/easyaudit/changes_history.html',
            context
        )
