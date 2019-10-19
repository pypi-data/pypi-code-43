from django.contrib import admin

# from django_audit_fields.admin import audit_fieldset_tuple

from ..admin_site import meta_subject_admin
from ..models import MalariaRapidTest
from .modeladmin import CrfModelAdmin


@admin.register(MalariaRapidTest, site=meta_subject_admin)
class MalariaRapidTestAdmin(CrfModelAdmin):

    pass
