from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from schools.models import School, Authority, Faculty



class SchoolResource(resources.ModelResource):

    authority = fields.Field(
        column_name='authority',
        attribute='authority',
        widget=ForeignKeyWidget(Authority, 'authority_name')
    )

    class Meta:
        model = School

class SchoolAdmin(ImportExportModelAdmin):
    resource_class = SchoolResource
    readonly_fields = ('id',)

    def get_list_display(self, request):
        return('school_name', 'authority', 'account_expiry')

class FacultyAdmin(ImportExportModelAdmin):
    pass


class AuthorityAdmin(ImportExportModelAdmin):
    pass



admin.site.register(School, SchoolAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Authority, AuthorityAdmin)

