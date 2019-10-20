import logging

from django.contrib import admin
from django.contrib.admin.models import (
    ADDITION,
    CHANGE,
    DELETION,
)
from django.utils.translation import ugettext_lazy as _

from ...utils import console

__all__ = ['LogEntryActionFlagListFilter']

console = console(source=__name__)
logger = logging.getLogger('app')


ACTION_FLAGS = {ADDITION: _('Add'), CHANGE: _('Change'), DELETION: _('Delete')}


class LogEntryActionFlagListFilter(admin.SimpleListFilter):
    title = _('Action')
    parameter_name = 'action_flag'

    def lookups(self, request, model_admin):
        return [(action, name) for action, name in ACTION_FLAGS.items()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(action_flag=self.value())
        return queryset
