from django.test import TestCase, tag
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_reference.reference_model_config import ReferenceModelConfig
from edc_reference.reference_model_config import (
    ReferenceFieldValidationError,
    ReferenceDuplicateField,
)
from edc_reference.reference_model_config import ReferenceModelValidationError
from edc_reference.site_reference import site_reference_configs
from edc_reference.site_reference import AlreadyRegistered
from edc_reference.site_reference import (
    SiteReferenceConfigError,
    ReferenceConfigNotRegistered,
)
from reference_app.visit_schedules import visit_schedule
from reference_app.reference_model_configs import register_configs


class TestSite(TestCase):
    def tearDown(self):
        register_configs()

    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)
        site_reference_configs.registry = {}
        site_reference_configs.loaded = False

    def test_site_register(self):
        name = "reference_app.crfone"
        fields = ["field_date", "field_datetime", "field_int", "field_str"]
        reference_config = ReferenceModelConfig(fields=fields, name=name)
        site_reference_configs.register(reference_config=reference_config)
        self.assertEqual(fields, site_reference_configs.get_fields(name=name))

    def test_site_reregister(self):
        name = "reference_app.crfone"
        reference_config = ReferenceModelConfig(
            name=name, fields=["field_date", "field_datetime", "field_int", "field_str"]
        )
        site_reference_configs.register(reference_config=reference_config)
        self.assertRaises(
            AlreadyRegistered,
            site_reference_configs.register,
            reference_config=reference_config,
        )

    def test_check_ok(self):
        name = "reference_app.crfone"
        fields = ["field_str", "field_date", "field_datetime", "field_int"]
        site_reference_configs.registry = {}
        reference = ReferenceModelConfig(fields=fields, name=name)
        try:
            reference.check()
        except (ReferenceFieldValidationError, ReferenceModelValidationError) as e:
            self.fail(f"Reference validation error unexpectedly raised. Got{e}")

    def test_check_ok2(self):
        name = "reference_app.crfone"
        reference_config = ReferenceModelConfig(
            fields=["field_str", "field_date", "field_datetime", "field_int"], name=name
        )
        site_reference_configs.register(reference_config=reference_config)
        site_reference_configs.check()

    def test_check_bad_model(self):
        name = "reference_app.erik"
        fields = ["f1"]
        reference_config = ReferenceModelConfig(fields=fields, name=name)
        self.assertRaises(ReferenceModelValidationError, reference_config.check)

    def test_check_bad_fields(self):
        name = "reference_app.crfone"
        fields = ["f1"]
        site_reference_configs.registry = {}
        reference_config = ReferenceModelConfig(fields=fields, name=name)
        self.assertRaises(ReferenceFieldValidationError, reference_config.check)

    def test_raises_on_duplicate_field_name(self):
        name = "reference_app.crfone"
        fields = ["f1", "f1"]
        self.assertRaises(
            ReferenceDuplicateField, ReferenceModelConfig, fields=fields, name=name
        )

    def test_not_registered_for_fields(self):
        name = "reference_app.crfone"
        site_reference_configs.registry = {}
        self.assertRaises(
            SiteReferenceConfigError, site_reference_configs.get_fields, name=name
        )

    def test_not_registered_for_reference_model(self):
        name = "reference_app.crfone"
        site_reference_configs.registry = {}
        self.assertRaises(
            SiteReferenceConfigError,
            site_reference_configs.get_reference_model,
            name=name,
        )

    def test_not_registered_for_reregister(self):
        name = "reference_app.crfone"
        fields = ["f1"]
        reference_config = ReferenceModelConfig(fields=fields, name=name)
        site_reference_configs.registry = {}
        self.assertRaises(
            ReferenceConfigNotRegistered,
            site_reference_configs.reregister,
            reference_config,
        )

    def test_get_config(self):
        site_reference_configs.registry = {}
        name = "reference_app.crfone"
        fields = ["f1"]
        reference_config = ReferenceModelConfig(fields=fields, name=name)
        site_reference_configs.register(reference_config)
        self.assertEqual(
            reference_config,
            site_reference_configs.get_config(name="reference_app.crfone"),
        )
        self.assertRaises(
            SiteReferenceConfigError, site_reference_configs.get_config, name=None
        )

    def test_register_reference_models_from_visit_schedule(self):
        site_reference_configs.registry = {}
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "reference_app.subjectvisit"}
        )
        self.assertTrue(site_reference_configs.get_config(name="reference_app.crfone"))

    def test_reregister_reference_models_from_visit_schedule(self):
        site_reference_configs.registry = {}
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "reference_app.subjectvisit"}
        )
        # do again
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "reference_app.subjectvisit"}
        )
        self.assertTrue(site_reference_configs.get_config(name="reference_app.crfone"))

    def test_add_fields_to_reference_config(self):
        name = "reference_app.crfone"
        fields = ["f1"]
        site_reference_configs.registry = {}
        reference_config = ReferenceModelConfig(fields=fields, name=name)
        site_reference_configs.register(reference_config)
        self.assertEqual(reference_config.field_names, ["f1"])
        site_reference_configs.add_fields_to_config(name=name, fields=["f2", "f3"])
        self.assertEqual(reference_config.field_names, ["f1", "f2", "f3"])
