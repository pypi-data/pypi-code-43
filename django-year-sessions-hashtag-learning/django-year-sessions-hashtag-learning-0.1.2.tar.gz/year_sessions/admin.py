from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from year_sessions.models import YearSession

class YearSessionAdmin(ImportExportModelAdmin):
    readonly_fields = ('id',)

admin.site.register(YearSession, YearSessionAdmin)