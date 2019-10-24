from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_reference.models import Reference
from edc_reference.refsets import (
    LongitudinalRefsets,
    InvalidOrdering,
    NoRefsetObjectsExist,
)
from edc_utils import get_utcnow
from edc_visit_tracking.constants import SCHEDULED
from reference_app.models import SubjectVisit, CrfOne, SubjectConsent
from reference_app.visit_schedules import visit_schedule


class TestLongitudinal(TestCase):
    def setUp(self):
        self.subject_identifier = "12345"

        values = [
            ("NEG", get_utcnow() - relativedelta(years=3)),
            ("POS", get_utcnow() - relativedelta(years=2)),
            ("POS", get_utcnow() - relativedelta(years=1)),
        ]

        dte = get_utcnow()

        SubjectConsent.objects.create(
            consent_datetime=dte - relativedelta(days=10),
            subject_identifier=self.subject_identifier,
            identity="012345678",
            confirm_identity="012345678",
        )

        for index, days in [(1, 14), (2, 7), (3, 0)]:
            appointment = Appointment.objects.create(
                subject_identifier=self.subject_identifier,
                appt_datetime=dte - relativedelta(days=days),
                timepoint_datetime=dte - relativedelta(days=index),
                visit_schedule_name=visit_schedule.name,
                schedule_name="schedule",
                visit_code=f"{index}000",
                timepoint=Decimal(f"{index-1}.0"),
            )
            SubjectVisit.objects.create(
                appointment=appointment,
                subject_identifier=self.subject_identifier,
                report_datetime=dte - relativedelta(days=days),
                reason=SCHEDULED,
            )

        for index, subject_visit in enumerate(
            SubjectVisit.objects.filter(
                subject_identifier=self.subject_identifier
            ).order_by("report_datetime")
        ):
            CrfOne.objects.create(
                subject_visit=subject_visit,
                report_datetime=subject_visit.report_datetime,
                field_str=values[index][0],
                field_datetime=values[index][1],
            )

    def test_longitudinal_refsets(self):
        refsets = LongitudinalRefsets(
            subject_identifier=self.subject_identifier,
            visit_model="reference_app.subjectvisit",
            name="reference_app.crfone",
            reference_model_cls=Reference,
        )
        self.assertEqual(
            [refset.timepoint for refset in refsets],
            [Decimal("0.0"), Decimal("1.0"), Decimal("2.0")],
        )

    def test_longitudinal_refset_uses_subject_visit_report_datetime(self):
        longitudinal_refsets = LongitudinalRefsets(
            subject_identifier=self.subject_identifier,
            visit_model="reference_app.subjectvisit",
            name="reference_app.crfone",
            reference_model_cls=Reference,
        )
        subject_visits = SubjectVisit.objects.filter(
            subject_identifier=self.subject_identifier
        ).order_by("report_datetime")
        report_datetimes = [obj.report_datetime for obj in subject_visits]
        self.assertEqual(
            [ref.report_datetime for ref in longitudinal_refsets], report_datetimes
        )
        self.assertEqual(
            [v.report_datetime for v in longitudinal_refsets.visit_references],
            report_datetimes,
        )

    def test_no_refsets(self):
        refsets = LongitudinalRefsets(
            subject_identifier=self.subject_identifier,
            visit_model="reference_app.subjectvisit",
            name="reference_app.crfone",
            reference_model_cls=Reference,
        )
        refsets._refsets = []
        self.assertRaises(NoRefsetObjectsExist, refsets.fieldset, "field_name")

    def test_ordering(self):
        refsets = LongitudinalRefsets(
            subject_identifier=self.subject_identifier,
            visit_model="reference_app.subjectvisit",
            name="reference_app.crfone",
            reference_model_cls=Reference,
        ).order_by("-report_datetime")
        self.assertEqual(
            [ref.timepoint for ref in refsets],
            [Decimal("2.0"), Decimal("1.0"), Decimal("0.0")],
        )
        refsets.order_by("-timepoint")
        self.assertEqual(
            [ref.timepoint for ref in refsets],
            [Decimal("2.0"), Decimal("1.0"), Decimal("0.0")],
        )
        refsets.order_by("report_datetime")
        self.assertEqual(
            [ref.timepoint for ref in refsets],
            [Decimal("0.0"), Decimal("1.0"), Decimal("2.0")],
        )
        refsets.order_by("timepoint")
        self.assertEqual(
            [ref.timepoint for ref in refsets],
            [Decimal("0.0"), Decimal("1.0"), Decimal("2.0")],
        )

    def test_bad_ordering(self):
        self.assertRaises(
            InvalidOrdering,
            LongitudinalRefsets(
                subject_identifier=self.subject_identifier,
                visit_model="reference_app.subjectvisit",
                name="reference_app.crfone",
                reference_model_cls=Reference,
            ).order_by,
            "blah",
        )

    def test_get(self):
        refset = LongitudinalRefsets(
            subject_identifier=self.subject_identifier,
            visit_model="reference_app.subjectvisit",
            name="reference_app.crfone",
            reference_model_cls=Reference,
        )
        self.assertEqual(
            refset.fieldset("field_str").all().values, ["NEG", "POS", "POS"]
        )
        self.assertEqual(
            refset.fieldset("field_str").all().order_by("-report_datetime").values,
            ["POS", "POS", "NEG"],
        )

    def test_get2(self):
        refsets = LongitudinalRefsets(
            subject_identifier=self.subject_identifier,
            visit_model="reference_app.subjectvisit",
            name="reference_app.crfone",
            reference_model_cls=Reference,
        )
        self.assertEqual(
            refsets.fieldset("field_str").all().order_by("field_datetime").values,
            ["NEG", "POS", "POS"],
        )
        self.assertEqual(
            refsets.fieldset("field_str").order_by("-field_datetime").all().values,
            ["POS", "POS", "NEG"],
        )

    def test_get_last(self):
        refsets = LongitudinalRefsets(
            subject_identifier=self.subject_identifier,
            visit_model="reference_app.subjectvisit",
            name="reference_app.crfone",
            reference_model_cls=Reference,
        )
        self.assertEqual(
            refsets.fieldset("field_str").order_by("field_datetime").last(), "POS"
        )
        self.assertEqual(
            refsets.fieldset("field_str").order_by("-field_datetime").last(), "NEG"
        )

    def test_repr(self):
        refsets = LongitudinalRefsets(
            subject_identifier=self.subject_identifier,
            visit_model="reference_app.subjectvisit",
            name="reference_app.crfone",
            reference_model_cls=Reference,
        )
        self.assertTrue(repr(refsets))
        for refset in refsets:
            self.assertTrue(repr(refset))

    def test_with_model_name(self):
        refsets = LongitudinalRefsets(
            subject_identifier=self.subject_identifier,
            visit_model="reference_app.subjectvisit",
            name="reference_app.crfone",
            reference_model_cls="edc_reference.reference",
        )
        self.assertTrue(repr(refsets))
        for refset in refsets:
            self.assertTrue(repr(refset))
