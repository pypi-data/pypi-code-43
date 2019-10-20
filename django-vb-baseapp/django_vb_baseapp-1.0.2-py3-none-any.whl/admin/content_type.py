import logging

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from console import console

__all__ = ['ContentTypeAdmin']

console = console(source=__name__)
logger = logging.getLogger('app')


@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    search_fields = ['model']
    ordering = ['model']
