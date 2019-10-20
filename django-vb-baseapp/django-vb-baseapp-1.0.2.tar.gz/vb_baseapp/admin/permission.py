import logging

from django.contrib import admin
from django.contrib.auth.models import Permission

from console import console

__all__ = ['PermissionAdmin']

console = console(source=__name__)
logger = logging.getLogger('app')


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['content_type']
    list_select_related = ['content_type']
    autocomplete_fields = ['content_type']
    ordering = ['content_type__model']
