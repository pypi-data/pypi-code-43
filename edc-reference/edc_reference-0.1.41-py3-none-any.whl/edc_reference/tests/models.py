# from django.db import models
# from django.db.models.deletion import PROTECT
# from edc_lab.model_mixins import PanelModelMixin
# from edc_model.models import BaseUuidModel
# from edc_utils import get_utcnow
#
# from ..model_mixins import ReferenceModelMixin, RequisitionReferenceModelMixin
# from edc_visit_tracking.model_mixins.visit_model_mixin.visit_model_mixin import VisitModelMixin
#
#
# class CrfModelMixin(models.Model):
#     @property
#     def visit(self):
#         return self.subject_visit
#
#     class Meta:
#         abstract = True
#
#
# class SubjectVisit(VisitModelMixin, ReferenceModelMixin, BaseUuidModel):
#
#     # subject_identifier = models.CharField(max_length=50)
#
#     # report_datetime = models.DateTimeField(default=get_utcnow)
#
#     # visit_code = models.CharField(max_length=50)
#     pass
#
#
# class SubjectRequisition(
#     CrfModelMixin, PanelModelMixin, RequisitionReferenceModelMixin, BaseUuidModel
# ):
#
#     subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)
#
#     report_datetime = models.DateTimeField(default=get_utcnow)
#
#     panel_name = models.CharField(max_length=50)
#
#
# class TestModel(CrfModelMixin, ReferenceModelMixin, BaseUuidModel):
#
#     subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)
#
#     report_datetime = models.DateTimeField(default=get_utcnow)
#
#     field_str = models.CharField(max_length=50)
#
#
# class TestModelBad(CrfModelMixin, BaseUuidModel):
#
#     subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)
#
#     report_datetime = models.DateTimeField(default=get_utcnow)
#
#     field_str = models.CharField(max_length=50)
#
#
# class CrfOne(CrfModelMixin, ReferenceModelMixin, BaseUuidModel):
#
#     subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)
#
#     report_datetime = models.DateTimeField(default=get_utcnow)
#
#     field_str = models.CharField(max_length=50)
#
#     field_date = models.DateField(null=True)
#
#     field_datetime = models.DateTimeField(null=True)
#
#     field_int = models.IntegerField(null=True)
#
#
# class CrfWithBadField(CrfModelMixin, ReferenceModelMixin, BaseUuidModel):
#
#     subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)
#
#     report_datetime = models.DateTimeField(default=get_utcnow)
#
#     field_str = models.CharField(max_length=50)
#
#     field_date = models.DateField(null=True)
#
#     field_datetime = models.DateTimeField(null=True)
#
#     field_int = models.IntegerField(null=True)
#
#
# class CrfWithDuplicateField(CrfModelMixin, ReferenceModelMixin, BaseUuidModel):
#
#     subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)
#
#     report_datetime = models.DateTimeField(default=get_utcnow)
#
#     field_str = models.CharField(max_length=50)
#
#     field_date = models.DateField(null=True)
#
#     field_datetime = models.DateTimeField(null=True)
#
#     field_int = models.IntegerField(null=True)
#
#
# class CrfWithUnknownDatatype(CrfModelMixin, ReferenceModelMixin, BaseUuidModel):
#
#     subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)
#
#     report_datetime = models.DateTimeField(default=get_utcnow)
#
#     field_decimal = models.DecimalField(decimal_places=2, max_digits=10)
