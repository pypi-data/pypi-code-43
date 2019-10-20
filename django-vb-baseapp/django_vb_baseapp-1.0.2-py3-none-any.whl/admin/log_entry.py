import logging

from django.contrib import admin
from django.contrib.admin.models import LogEntry

from console import console

from .filters import LogEntryActionFlagListFilter

__all__ = ['LogEntryAdmin']

console = console(source=__name__)
logger = logging.getLogger('app')


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'object_repr', 'action_time']
    list_select_related = ['content_type']
    list_filter = [LogEntryActionFlagListFilter]
    search_fields = ['object_repr']
    autocomplete_fields = ['user', 'content_type']
