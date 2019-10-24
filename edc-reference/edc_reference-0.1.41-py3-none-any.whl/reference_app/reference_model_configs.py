from edc_reference import ReferenceModelConfig, site_reference_configs


def register_configs():
    site_reference_configs.registry = {}
    site_reference_configs.loaded = False

    site_reference_configs.register_from_visit_schedule(
        visit_models={
            'edc_appointment.appointment': 'reference_app.subjectvisit'})

    reference_config = ReferenceModelConfig(
        name="reference_app.testmodel", fields=["field_str", "report_datetime"]
    )
    site_reference_configs.register(reference_config)

    reference_config = ReferenceModelConfig(
        name="reference_app.subjectrequisition.cd4", fields=["panel"]
    )
    site_reference_configs.register(reference_config)

    reference_config = ReferenceModelConfig(
        name="reference_app.subjectrequisition.vl", fields=["panel"]
    )
    site_reference_configs.register(reference_config)

    reference_config = ReferenceModelConfig(
        name="reference_app.subjectrequisition.wb", fields=["panel"]
    )
    site_reference_configs.register(reference_config)

    configs = {
        'reference_app.crfone': ["field_str",
                                 "field_date",
                                 "field_datetime",
                                 "field_int", ],
    }

    for reference_name, fields in configs.items():
        site_reference_configs.add_fields_to_config(
            name=reference_name, fields=fields)


register_configs()
