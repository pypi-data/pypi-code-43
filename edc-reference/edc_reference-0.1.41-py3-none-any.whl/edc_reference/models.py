from django.core.exceptions import FieldError
from django.db import models
from edc_model.models import BaseUuidModel
from edc_sites.models import CurrentSiteManager, SiteModelMixin

from .managers import ReferenceManager


class ReferenceFieldDatatypeNotFound(Exception):
    pass


class Reference(SiteModelMixin, BaseUuidModel):

    identifier = models.CharField(max_length=50)

    visit_schedule_name = models.CharField(max_length=150, null=True)

    schedule_name = models.CharField(max_length=150, null=True)

    visit_code = models.CharField(max_length=150, null=True)

    visit_code_sequence = models.IntegerField(null=True)

    timepoint = models.DecimalField(decimal_places=1, max_digits=6, null=True)

    report_datetime = models.DateTimeField()

    model = models.CharField(max_length=250)

    field_name = models.CharField(max_length=50)

    datatype = models.CharField(max_length=50)

    value_str = models.CharField(max_length=50, null=True)

    value_int = models.IntegerField(null=True)

    value_date = models.DateField(null=True)

    value_datetime = models.DateTimeField(null=True)

    value_uuid = models.UUIDField(null=True)

    related_name = models.CharField(max_length=100, null=True)

    objects = ReferenceManager()

    on_site = CurrentSiteManager()

    def __str__(self):
        return (
            f"{self.identifier} {self.visit_schedule_name}.{self.schedule_name}."
            f"{self.visit_code}.{self.visit_code_sequence}@{self.timepoint} "
            f"{self.model}.{self.field_name}={self.value}"
        )

    def save(self, *args, **kwargs):
        if not self.visit_schedule_name:
            raise FieldError("visit_schedule_name cannot be None")
        if not self.schedule_name:
            raise FieldError("schedule_name cannot be None")
        if not self.visit_code:
            raise FieldError("visit_code cannot be None")
        if not self.visit_code:
            raise FieldError("visit_code cannot be None")
        if self.timepoint is None:
            raise FieldError("timepoint cannot be None")
        super().save(*args, **kwargs)

    def natural_key(self):
        return (
            self.identifier,
            self.visit_schedule_name,
            self.schedule_name,
            self.visit_code,
            self.timepoint,
            self.report_datetime,
            self.model,
            self.field_name,
        )

    natural_key.dependencies = ["sites.Site"]

    def update_value(
        self, value=None, internal_type=None, field=None, related_name=None, site=None
    ):
        """Updates the correct `value` field based on the
        field class datatype.
        """
        internal_type = internal_type or field.get_internal_type()
        if internal_type in ["ForeignKey", "OneToOneField"]:
            self.datatype = "UUIDField"
        else:
            self.datatype = internal_type
        update = None
        value_fields = [
            fld for fld in self._meta.get_fields() if fld.name.startswith("value")
        ]
        for fld in value_fields:
            if fld.name.startswith("value"):  # e.g. value_str, value_int, etc
                if fld.get_internal_type() == self.datatype:
                    update = (fld.name, value)
                    break
        if update:
            self.related_name = related_name
            setattr(self, *update)
            for fld in value_fields:
                if fld.name != update[0]:
                    setattr(self, fld.name, None)
        else:
            raise ReferenceFieldDatatypeNotFound(
                f"Reference field internal_type not found. Got '{self.datatype}'. "
                f"model={self.model}.{self.field_name} "
                f"Expected a django.models.field internal type like 'CharField', "
                "'DateTimeField', etc."
            )
        if site is not None:
            self.site = site
        self.save()

    @property
    def value(self):
        for field_name in [
            "value_str",
            "value_int",
            "value_date",
            "value_datetime",
            "value_uuid",
        ]:
            value = getattr(self, field_name)
            if value is not None:
                break
        return value

    class Meta:
        unique_together = [
            "identifier",
            "visit_schedule_name",
            "schedule_name",
            "visit_code",
            "visit_code_sequence",
            "timepoint",
            "report_datetime",
            "model",
            "field_name",
        ]
        ordering = (
            "identifier",
            "report_datetime",
            "visit_schedule_name",
            "schedule_name",
            "timepoint",
            "model",
            "field_name",
        )
        indexes = [
            models.Index(
                fields=[
                    "identifier",
                    "visit_schedule_name",
                    "schedule_name",
                    "visit_code",
                    "timepoint",
                    "model",
                    "field_name",
                ]
            )
        ]
