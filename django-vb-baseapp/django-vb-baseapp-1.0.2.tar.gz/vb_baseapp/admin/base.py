import logging

from django.contrib import admin
from django.db import models
from django.forms import TextInput
from django.utils.translation import ugettext_lazy as _

from console import console

from ..widgets import AdminImageFileWidget
from .actions import hard_delete_selected, recover_selected

__all__ = ['CustomBaseModelAdmin', 'CustomBaseModelAdminWithSoftDelete']

console = console(source=__name__)
logger = logging.getLogger('app')


class CustomBaseModelAdmin(admin.ModelAdmin):
    """

    Base model admin for BaseModel

    """

    sticky_list_filter = ('status',)

    formfield_overrides = {
        models.ImageField: {'widget': AdminImageFileWidget},
        models.CharField: {'widget': TextInput(attrs={'size': 100})},
    }

    def get_list_filter(self, request):
        list_filter = list(super().get_list_filter(request))
        if self.sticky_list_filter:
            list_filter = list(self.sticky_list_filter) + list(list_filter)
        return list_filter


class CustomBaseModelAdminWithSoftDelete(CustomBaseModelAdmin):

    hide_deleted_at = True

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.GET:
            return queryset
        return queryset.all()

    def get_exclude(self, request, obj=None):
        excluded = super().get_exclude(request, obj=obj)
        exclude = [] if excluded is None else list(excluded)
        if self.hide_deleted_at:
            exclude.append('deleted_at')
        return exclude

    def get_actions(self, request):
        existing_actions = super().get_actions(request)
        existing_actions.update(
            dict(
                recover_selected=(recover_selected, 'recover_selected', _('Recover selected %(verbose_name_plural)s'))
            )
        )
        existing_actions.update(
            dict(
                hard_delete_selected=(
                    hard_delete_selected,
                    'hard_delete_selected',
                    _('Hard delete selected %(verbose_name_plural)s'),
                )
            )
        )
        return existing_actions
