from django.contrib import admin
from edc_adverse_event.modeladmin_mixins import DeathReportModelAdminMixin
from edc_model_admin import SimpleHistoryAdmin

from ..admin_site import meta_ae_admin
from ..forms import DeathReportForm
from ..models import DeathReport


@admin.register(DeathReport, site=meta_ae_admin)
class DeathReportAdmin(DeathReportModelAdminMixin, SimpleHistoryAdmin):

    form = DeathReportForm
