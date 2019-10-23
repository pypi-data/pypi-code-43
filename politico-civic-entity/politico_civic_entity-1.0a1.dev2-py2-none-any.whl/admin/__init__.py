# Imports from Django.
from django.contrib import admin


# Imports from entity.
from entity.models import ImageTag
from entity.models import Organization
from entity.models import OrganizationClassification
from entity.models import OrganizationImage
from entity.models import Person
from entity.models import PersonImage
from entity.admin.person import PersonAdmin
from entity.admin.organization import OrganizationAdmin


admin.site.register(ImageTag)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationImage)
admin.site.register(OrganizationClassification)
admin.site.register(Person, PersonAdmin)
admin.site.register(PersonImage)
