from edc_adverse_event.model_mixins import DeathReportModelMixin
from edc_model.models import BaseUuidModel

from .model_mixins import MetaDeathReportModelMixin


class DeathReport(MetaDeathReportModelMixin, DeathReportModelMixin, BaseUuidModel):
    class Meta(DeathReportModelMixin.Meta):
        pass
