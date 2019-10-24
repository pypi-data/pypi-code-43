from django.db import models
from django.db.models.deletion import PROTECT
from edc_lab.model_mixins import PanelModelMixin
from edc_model.models import BaseUuidModel
from edc_utils import get_utcnow
from edc_reference.model_mixins import ReferenceModelMixin, RequisitionReferenceModelMixin
from edc_visit_tracking.model_mixins.visit_model_mixin.visit_model_mixin import VisitModelMixin
from edc_visit_schedule.model_mixins.on_schedule_model_mixin import OnScheduleModelMixin
from edc_visit_schedule.model_mixins.off_schedule_model_mixin import OffScheduleModelMixin
from edc_offstudy.model_mixins.offstudy_model_mixin import OffstudyModelMixin
from edc_sites.models import SiteModelMixin, CurrentSiteManager
from edc_identifier.model_mixins.subject_identifier_model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_identifier.managers import SubjectIdentifierManager
from edc_consent.model_mixins.consent_model_mixin import ConsentModelMixin
from edc_consent.field_mixins.personal_fields_mixin import PersonalFieldsMixin
from edc_consent.field_mixins.identity_fields_mixin import IdentityFieldsMixin
from edc_registration.model_mixins.updates_or_creates_registered_subject_model_mixin import UpdatesOrCreatesRegistrationModelMixin
from edc_metadata.model_mixins.creates.creates_metadata_model_mixin import CreatesMetadataModelMixin


class OnSchedule(OnScheduleModelMixin, BaseUuidModel):

    pass


class OffSchedule(OffScheduleModelMixin, BaseUuidModel):

    pass


class SubjectOffstudy(OffstudyModelMixin, BaseUuidModel):
    class Meta(OffstudyModelMixin.Meta):
        pass


class DeathReport(UniqueSubjectIdentifierFieldMixin, SiteModelMixin, BaseUuidModel):

    objects = SubjectIdentifierManager()

    def natural_key(self):
        return (self.subject_identifier,)


class SubjectConsent(
    ConsentModelMixin,
    PersonalFieldsMixin,
    IdentityFieldsMixin,
    UniqueSubjectIdentifierFieldMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):

    on_site = CurrentSiteManager()

    objects = SubjectIdentifierManager()

    def natural_key(self):
        return (self.subject_identifier,)


class SubjectVisit(
    VisitModelMixin,
    ReferenceModelMixin,
    CreatesMetadataModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):

    on_site = CurrentSiteManager()


class CrfModelMixin(SiteModelMixin, models.Model):
    on_site = CurrentSiteManager()

    @property
    def visit(self):
        return self.subject_visit

    @property
    def subject_identifier(self):
        return self.subject_visit.subject_identifier

    class Meta:
        abstract = True


class SubjectRequisition(
    CrfModelMixin, PanelModelMixin, RequisitionReferenceModelMixin, BaseUuidModel
):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    panel_name = models.CharField(max_length=50)


class TestModel(CrfModelMixin, ReferenceModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    field_str = models.CharField(max_length=50)


class TestModelBad(CrfModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    field_str = models.CharField(max_length=50)


class CrfOne(CrfModelMixin, ReferenceModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    field_str = models.CharField(max_length=50)

    field_date = models.DateField(null=True)

    field_datetime = models.DateTimeField(null=True)

    field_int = models.IntegerField(null=True)


class CrfWithBadField(CrfModelMixin, ReferenceModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    field_str = models.CharField(max_length=50)

    field_date = models.DateField(null=True)

    field_datetime = models.DateTimeField(null=True)

    field_int = models.IntegerField(null=True)


class CrfWithDuplicateField(CrfModelMixin, ReferenceModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    field_str = models.CharField(max_length=50)

    field_date = models.DateField(null=True)

    field_datetime = models.DateTimeField(null=True)

    field_int = models.IntegerField(null=True)


class CrfWithUnknownDatatype(CrfModelMixin, ReferenceModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    field_decimal = models.DecimalField(decimal_places=2, max_digits=10)
