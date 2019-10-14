from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from activity.models import Process
from activity.models import Activity


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name_plural = _('Processes')


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name_plural = _('Activities')
