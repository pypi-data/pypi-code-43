from django.test import TestCase, tag
from edc_reference.models import Reference
from edc_utils import get_utcnow
from decimal import Decimal


class TestModel(TestCase):

    reference_model_cls = Reference
    subject_identifier = "11111"
    visit_schedule_name = "visit_schedule"
    schedule_name = "schedule"

    def test_model_update(self):
        reference = self.reference_model_cls.objects.create(
            model=f"reference_app.testmodel",
            identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.schedule_name,
            visit_code="1000",
            timepoint=Decimal("1.0"),
            field_name="field_name",
        )
        reference.update_value(value="5", internal_type="CharField")
        self.assertEqual(
            self.reference_model_cls.objects.get(id=reference.id).value, "5"
        )
        self.assertEqual(
            self.reference_model_cls.objects.get(id=reference.id).value_str, "5"
        )
