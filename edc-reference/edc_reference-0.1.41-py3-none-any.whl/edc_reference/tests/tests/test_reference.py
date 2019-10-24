from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_lab.models.panel import Panel
from edc_reference.models import Reference, ReferenceFieldDatatypeNotFound
from edc_reference.reference import (
    ReferenceDeleter,
    ReferenceGetter,
    ReferenceGetterError,
    ReferenceObjectDoesNotExist,
    ReferenceUpdater,
    ReferenceFieldNotFound,
)
from edc_reference.reference_model_config import (
    ReferenceDuplicateField,
    ReferenceFieldValidationError,
    ReferenceModelConfig,
)
from edc_reference.site_reference import site_reference_configs
from edc_utils import get_utcnow
from edc_visit_tracking.constants import SCHEDULED
from reference_app.models import CrfOne, SubjectVisit, SubjectConsent
from reference_app.models import CrfWithUnknownDatatype, TestModel, SubjectRequisition
from reference_app.reference_model_configs import register_configs
from reference_app.visit_schedules import visit_schedule


class TestReferenceModel(TestCase):
    def setUp(self):
        self.panel_cd4 = Panel.objects.create(name="cd4")
        self.panel_vl = Panel.objects.create(name="vl")
        self.panel_wb = Panel.objects.create(name="wb")
        self.subject_identifier = "123456789"

        dte = get_utcnow()

        SubjectConsent.objects.create(
            consent_datetime=dte,
            subject_identifier=self.subject_identifier,
            identity="012345678",
            confirm_identity="012345678",
        )

        appointment = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            appt_datetime=dte,
            timepoint_datetime=dte,
            visit_schedule_name=visit_schedule.name,
            schedule_name="schedule",
            visit_code="1000",
            timepoint=Decimal("1.0"),
        )

        self.subject_visit = SubjectVisit.objects.create(
            appointment=appointment, reason=SCHEDULED
        )

    def reset_site_reference_configs(self):
        site_reference_configs.registry = {}
        site_reference_configs.loaded = False
        site_reference_configs.registered_from_visit_schedules = False

        subjectvisit_reference = ReferenceModelConfig(
            name="reference_app.subjectvisit", fields=["report_datetime", "visit_code"]
        )

        self.testmodel_reference = ReferenceModelConfig(
            name="reference_app.testmodel", fields=["field_str", "report_datetime"]
        )
        self.crfone_reference = ReferenceModelConfig(
            name="reference_app.crfone",
            fields=[
                "field_str",
                "field_date",
                "field_datetime",
                "field_int",
                "report_datetime",
            ],
        )
        site_reference_configs.register(subjectvisit_reference)
        site_reference_configs.register(self.testmodel_reference)
        site_reference_configs.register(self.crfone_reference)

    def test_updater_repr(self):
        model_obj = TestModel.objects.create(
            subject_visit=self.subject_visit, field_str="erik"
        )
        self.assertTrue(repr(ReferenceUpdater(model_obj=model_obj)))

    def test_model_repr(self):
        model_obj = TestModel.objects.create(
            subject_visit=self.subject_visit, field_str="erik"
        )
        ReferenceUpdater(model_obj=model_obj)
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.timepoint,
            field_name="field_str",
        )
        self.assertTrue(repr(reference))

    def test_updater_creates_reference(self):
        model_obj = TestModel.objects.create(
            subject_visit=self.subject_visit, field_str="erik"
        )
        ReferenceUpdater(model_obj=model_obj)
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.timepoint,
            field_name="field_str",
        )
        self.assertEqual(reference.value, "erik")

    def test_updater_updates_reference(self):
        model_obj = TestModel.objects.create(
            subject_visit=self.subject_visit, field_str="erik"
        )
        ReferenceUpdater(model_obj=model_obj)
        model_obj.field_str = "bob"
        ReferenceUpdater(model_obj=model_obj)
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.timepoint,
            field_name="field_str",
        )
        self.assertEqual(reference.value, "bob")

    def test_updater_with_bad_field_name(self):
        site_reference_configs.add_fields_to_config(
            "reference_app.testmodel", fields=["blah"]
        )
        try:
            TestModel.objects.create(subject_visit=self.subject_visit, field_str="erik")
        except ReferenceFieldNotFound:
            pass
        else:
            self.fail("ReferenceFieldNotFound unexpectedly not raised")
        finally:
            site_reference_configs.remove_fields_from_config(
                "reference_app.testmodel", fields=["blah"]
            )

    def test_deleter(self):
        model_obj = TestModel.objects.create(
            subject_visit=self.subject_visit, field_str="erik"
        )
        ReferenceUpdater(model_obj=model_obj)
        model_obj.delete()
        ReferenceDeleter(model_obj=model_obj)
        try:
            reference = Reference.objects.get(
                identifier=self.subject_identifier,
                timepoint=self.subject_visit.timepoint,
                field_name="field_str",
            )
        except ObjectDoesNotExist:
            pass
        else:
            self.fail(f"Object unexpectedly exists. Got {reference}")

    def test_model_mixin_deleter(self):
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit, field_str="erik"
        )
        self.assertGreater(
            Reference.objects.filter(model="reference_app.crfone").count(), 2
        )
        crf_one.delete()
        self.assertEqual(
            0, Reference.objects.filter(model="reference_app.crfone").count()
        )

    def test_model_creates_reference(self):
        CrfOne.objects.create(subject_visit=self.subject_visit, field_str="erik")
        self.assertEqual(
            len(site_reference_configs.get_fields("reference_app.crfone")), 5
        )

        self.assertEqual(
            Reference.objects.filter(model="reference_app.crfone").count(), 5
        )

    def test_model_creates_reference2(self):
        CrfOne.objects.create(subject_visit=self.subject_visit, field_str="erik")
        try:
            reference = Reference.objects.get(
                identifier=self.subject_identifier,
                timepoint=self.subject_visit.timepoint,
                report_datetime=self.subject_visit.report_datetime,
                model="reference_app.crfone",
                field_name="field_str",
            )
        except ObjectDoesNotExist as e:
            self.fail(f"ObjectDoesNotExist unexpectedly raised. Got {e}")
        self.assertEqual(reference.value, "erik")

    def test_model_get_for_report_datetime(self):
        CrfOne.objects.create(subject_visit=self.subject_visit, field_str="erik")
        try:
            reference = Reference.objects.get(
                identifier=self.subject_identifier,
                timepoint=self.subject_visit.timepoint,
                report_datetime=self.subject_visit.report_datetime,
                model="reference_app.crfone",
                field_name="report_datetime",
            )
        except ObjectDoesNotExist as e:
            self.fail(f"ObjectDoesNotExist unexpectedly raised. Got {e}")
        self.assertEqual(reference.value, self.subject_visit.report_datetime)

    def test_model_updates_reference(self):
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit, field_str="erik"
        )
        crf_one.field_str = "bob"
        crf_one.save()
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.timepoint,
            report_datetime=self.subject_visit.report_datetime,
            field_name="field_str",
        )
        self.assertEqual(reference.value, "bob")

    def test_model_creates_for_date(self):
        dte = date.today()
        CrfOne.objects.create(subject_visit=self.subject_visit, field_date=dte)
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.timepoint,
            report_datetime=self.subject_visit.report_datetime,
            field_name="field_date",
        )
        self.assertEqual(reference.value, dte)

    def test_model_creates_for_datetime(self):
        dte = get_utcnow()
        CrfOne.objects.create(subject_visit=self.subject_visit, field_datetime=dte)
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.timepoint,
            report_datetime=self.subject_visit.report_datetime,
            field_name="field_datetime",
        )
        self.assertEqual(reference.value, dte)

    def test_model_creates_for_int(self):
        integer = 100
        CrfOne.objects.create(subject_visit=self.subject_visit, field_int=integer)
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.timepoint,
            report_datetime=self.subject_visit.report_datetime,
            field_name="field_int",
        )
        self.assertEqual(reference.value, integer)

    def test_model_creates_for_all(self):
        strval = "erik"
        integer = 100
        dte = date.today()
        dtetime = get_utcnow()
        field_datetime = dtetime - relativedelta(days=1)
        CrfOne.objects.create(
            subject_visit=self.subject_visit,
            report_datetime=dtetime - relativedelta(days=10),
            field_str=strval,
            field_int=integer,
            field_date=dte,
            field_datetime=field_datetime,
        )
        for field_name in site_reference_configs.get_fields("reference_app.crfone"):
            reference = Reference.objects.get(
                identifier=self.subject_identifier,
                model="reference_app.crfone",
                timepoint=self.subject_visit.timepoint,
                report_datetime=self.subject_visit.report_datetime,
                field_name=field_name,
            )
            self.assertIn(
                reference.value,
                [
                    strval,
                    integer,
                    dte,
                    field_datetime,
                    self.subject_visit.report_datetime,
                ],
                msg=f"field_name={field_name}",
            )

    def test_model_creates_and_gets_for_report_datetime(self):
        """Assert uses subject visit report_datetime and not
        CRF report_datetime for field_name='report_datetime'.
        """
        dtetime = get_utcnow()
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            report_datetime=get_utcnow() - relativedelta(days=10),
            field_datetime=dtetime,
        )
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            model="reference_app.crfone",
            timepoint=self.subject_visit.timepoint,
            report_datetime=self.subject_visit.report_datetime,
            field_name="report_datetime",
        )
        self.assertEqual(reference.value, self.subject_visit.report_datetime)

        getter = ReferenceGetter(field_name="report_datetime", model_obj=crf_one)
        self.assertEqual(getter.value, self.subject_visit.report_datetime)

    def test_model_create_handles_none(self):
        CrfOne.objects.create(subject_visit=self.subject_visit, field_int=None)
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.timepoint,
            report_datetime=self.subject_visit.report_datetime,
            field_name="field_int",
        )
        self.assertEqual(reference.value, None)

    def test_model_raises_on_duplicate_field_name(self):
        self.assertRaises(
            ReferenceDuplicateField,
            ReferenceModelConfig,
            name="reference_app.crfwithduplicatefield",
            fields=["field_int", "field_int", "field_datetime", "field_str"],
        )

    def test_model_raises_on_bad_field_name(self):
        reference_config = ReferenceModelConfig(
            name="reference_app.crfwithbadfield",
            fields=["blah1", "blah2", "blah3", "blah4"],
        )
        self.assertRaises(ReferenceFieldValidationError, reference_config.check)

    def test_model_raises_on_bad_field_name_checked_by_site(self):
        reference_config = ReferenceModelConfig(
            name="reference_app.crfwithbadfield",
            fields=["blah1", "blah2", "blah3", "blah4"],
        )
        site_reference_configs.register(reference_config)
        errors = site_reference_configs.check()
        self.assertIsNotNone(errors)

    def test_raises_on_missing_model_mixin(self):
        reference_config = ReferenceModelConfig(
            name="reference_app.TestModelBad", fields=["report_datetime"]
        )
        site_reference_configs.register(reference_config)
        errors = site_reference_configs.check()
        self.assertIsNotNone(errors)

    def test_model_raises_on_unknown_field_datatype(self):
        reference_config = ReferenceModelConfig(
            name="reference_app.CrfWithUnknownDatatype", fields=["field_decimal"]
        )
        site_reference_configs.register(reference_config)
        self.assertRaises(
            ReferenceFieldDatatypeNotFound,
            CrfWithUnknownDatatype.objects.create,
            subject_visit=self.subject_visit,
            field_decimal=3.2,
        )

    def test_getter_repr(self):
        crf_one = CrfOne.objects.create(subject_visit=self.subject_visit, field_int=100)
        reference = ReferenceGetter(field_name="field_int", model_obj=crf_one)
        self.assertTrue(repr(reference))

    def test_report_datetime_uses_visit_report_datetime(self):
        CrfOne.objects.create(subject_visit=self.subject_visit, field_int=100)
        report_datetimes = []
        for obj in Reference.objects.filter(model__icontains="crfone"):
            report_datetimes.append(obj.report_datetime)
        self.assertGreater(len(report_datetimes), 0)
        for report_datetime in report_datetimes:
            self.assertEqual(report_datetime, self.subject_visit.report_datetime)

    def test_reference_getter_sets_attr(self):
        integer = 100
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit, field_int=integer
        )
        reference = ReferenceGetter(field_name="field_int", model_obj=crf_one)
        self.assertEqual(reference.field_int, integer)

    def test_reference_getter_sets_attr_even_if_none(self):
        crf_one = CrfOne.objects.create(subject_visit=self.subject_visit)
        reference = ReferenceGetter(field_name="field_int", model_obj=crf_one)
        self.assertEqual(reference.field_int, None)

    def test_site_checks_no_fields_raises(self):
        name = "reference_app.crfone"
        site_reference_configs.registry = {}
        try:
            ReferenceModelConfig(fields=[], name=name)
        except ReferenceFieldValidationError:
            pass
        else:
            self.fail("ReferenceFieldValidationError unexpectedly not raised")
        finally:
            register_configs()

    def test_site_checks_no_fields_raises2(self):
        name = "reference_app.crfone"
        site_reference_configs.registry = {}
        try:
            ReferenceModelConfig(name=name)
        except ReferenceFieldValidationError:
            pass
        else:
            self.fail("ReferenceFieldValidationError unexpectedly not raised")
        finally:
            register_configs()

    def test_reference_getter_without_crf_type_model(self):
        integer = 100
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit, field_int=integer
        )
        reference = ReferenceGetter(
            name="reference_app.crfone", field_name="field_int", visit_obj=crf_one.visit
        )
        self.assertEqual(reference.field_int, integer)

    @tag("1")
    def test_reference_getter_without_using_model_obj(self):
        integer = 100
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_int=integer,
            report_datetime=self.subject_visit.report_datetime,
        )
        opts = dict(
            name="reference_app.crfone",
            field_name="field_int",
            subject_identifier=self.subject_identifier,
            report_datetime=crf_one.visit.report_datetime,
            visit_schedule_name=crf_one.visit.visit_schedule_name,
            schedule_name=crf_one.visit.schedule_name,
            visit_code=crf_one.visit.visit_code,
            visit_code_sequence=crf_one.visit.visit_code_sequence,
            timepoint=crf_one.visit.timepoint,
        )
        reference = ReferenceGetter(**opts)
        self.assertEqual(reference.field_int, integer)

    @tag("1")
    def test_reference_getter_without_using_model_obj_and_missing_visit_attr(self):
        integer = 100
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_int=integer,
            report_datetime=self.subject_visit.report_datetime,
        )
        opts = dict(
            name="reference_app.crfone",
            field_name="field_int",
            subject_identifier=self.subject_identifier,
            report_datetime=crf_one.visit.report_datetime,
            visit_schedule_name=crf_one.visit.visit_schedule_name,
            schedule_name=crf_one.visit.schedule_name,
            visit_code=crf_one.visit.visit_code,
            timepoint=crf_one.visit.timepoint,
        )
        reference = ReferenceGetter(**opts)
        self.assertEqual(reference.field_int, integer)

    @tag("1")
    def test_reference_getter_raises(self):
        """Assert raises if reference instance does not exist
        and not create.
        """
        opts = dict(
            name="reference_app.crfone",
            field_name="field_int",
            subject_identifier=self.subject_identifier,
            report_datetime=self.subject_visit.report_datetime,
        )
        self.assertRaises(ReferenceObjectDoesNotExist, ReferenceGetter, **opts)

    @tag("1")
    def test_reference_getter_raises_missing_visit_attrs_on_create(self):
        """Assert raises if not all visit attrs are provided for create.
        """
        opts = dict(
            name="reference_app.crfone",
            field_name="field_int",
            subject_identifier=self.subject_identifier,
            report_datetime=self.subject_visit.report_datetime,
        )
        self.assertRaises(ReferenceGetterError, ReferenceGetter, create=True, **opts)

    def test_reference_getter_with_bad_field_raises(self):
        integer = 100
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit, field_int=integer
        )
        self.assertRaises(
            ReferenceObjectDoesNotExist,
            reference=ReferenceGetter,
            name="reference_app.crfone",
            field_name="blah",
            model_obj=crf_one,
        )
        try:
            ReferenceGetter(
                field_name="blah", name="reference_app.crfone", model_obj=crf_one
            )
        except ReferenceObjectDoesNotExist:
            pass

    def test_reference_getter_doesnotexist(self):
        self.assertRaises(
            ReferenceObjectDoesNotExist,
            reference=ReferenceGetter,
            field_name="blah",
            model="reference_app.crfone",
            model_obj=self.subject_visit,
        )

    def test_model_manager_crf(self):
        strval = "erik"
        integer = 100
        dte = date.today()
        dtetime = get_utcnow()
        CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_str=strval,
            field_int=integer,
            field_date=dte,
            field_datetime=dtetime,
        )
        qs = Reference.objects.filter_crf_for_visit(
            "reference_app.crfone", self.subject_visit
        )
        self.assertEqual(qs.count(), 5)

    def test_model_manager_crf_by_field(self):
        strval = "erik"
        integer = 100
        dte = date.today()
        dtetime = get_utcnow()
        CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_str=strval,
            field_int=integer,
            field_date=dte,
            field_datetime=dtetime,
        )
        obj = Reference.objects.get_crf_for_visit(
            "reference_app.crfone", self.subject_visit, "field_str"
        )
        self.assertEqual(obj.value, "erik")
        obj = Reference.objects.get_crf_for_visit(
            "reference_app.crfone", self.subject_visit, "field_int"
        )
        self.assertEqual(obj.value, integer)
        obj = Reference.objects.get_crf_for_visit(
            "reference_app.crfone", self.subject_visit, "field_date"
        )
        self.assertEqual(obj.value, dte)
        obj = Reference.objects.get_crf_for_visit(
            "reference_app.crfone", self.subject_visit, "field_datetime"
        )
        self.assertEqual(obj.value, dtetime)
        obj = Reference.objects.get_crf_for_visit(
            "reference_app.crfone", self.subject_visit, "blah"
        )
        self.assertIsNone(obj)

    def test_model_manager_requisition(self):
        SubjectRequisition.objects.create(
            subject_visit=self.subject_visit, panel=self.panel_cd4
        )
        obj = Reference.objects.get_requisition_for_visit(
            "reference_app.subjectrequisition.cd4", self.subject_visit
        )
        self.assertEqual(obj.value, self.panel_cd4.id)
        obj = Reference.objects.get_requisition_for_visit(
            "reference_app.subjectrequisition.blah", self.subject_visit
        )
        self.assertIsNone(obj)

    def test_requisition_creates_two(self):
        SubjectRequisition.objects.create(
            subject_visit=self.subject_visit, panel=self.panel_cd4
        )
        SubjectRequisition.objects.create(
            subject_visit=self.subject_visit, panel=self.panel_vl
        )
        obj = Reference.objects.get_requisition_for_visit(
            "reference_app.subjectrequisition.vl", self.subject_visit
        )
        self.assertEqual(obj.value, self.panel_vl.id)
        obj = Reference.objects.get_requisition_for_visit(
            "reference_app.subjectrequisition.cd4", self.subject_visit
        )
        self.assertEqual(obj.value, self.panel_cd4.id)
        obj = Reference.objects.get_requisition_for_visit(
            "reference_app.subjectrequisition.blah", self.subject_visit
        )
        self.assertIsNone(obj)

    def test_requisition_creates2(self):
        SubjectRequisition.objects.create(
            subject_visit=self.subject_visit, panel=self.panel_vl
        )
        SubjectRequisition.objects.create(
            subject_visit=self.subject_visit, panel=self.panel_cd4
        )
        SubjectRequisition.objects.create(
            subject_visit=self.subject_visit, panel=self.panel_wb
        )

        for panel in [self.panel_cd4, self.panel_vl, self.panel_wb]:
            with self.subTest(panel=panel):
                Reference.objects.get(
                    model=f"reference_app.subjectrequisition.{panel.name}",
                    report_datetime=self.subject_visit.report_datetime,
                    timepoint=self.subject_visit.timepoint,
                    field_name="panel",
                    value_uuid=panel.id,
                )
