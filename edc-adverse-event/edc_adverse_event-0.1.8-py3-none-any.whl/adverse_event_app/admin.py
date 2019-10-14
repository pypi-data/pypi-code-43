from django.contrib import admin


from edc_adverse_event.modeladmin_mixins import (
    AeInitialModelAdminMixin,
    AeFollowupModelAdminMixin,
)
from edc_model_admin import SimpleHistoryAdmin
from adverse_event_app.models import AeFollowup, AeInitial


@admin.register(AeInitial)
class AeInitialAdmin(AeInitialModelAdminMixin, SimpleHistoryAdmin):
    pass


@admin.register(AeFollowup)
class AeFollowupAdmin(AeFollowupModelAdminMixin, SimpleHistoryAdmin):
    pass
