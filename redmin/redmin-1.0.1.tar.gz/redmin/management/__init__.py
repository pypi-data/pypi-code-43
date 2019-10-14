inited = False


def init_models(sender, **kwargs):
    global inited
    if not inited:
        inited = True
        from redmin.models.field import init_fields
        from redmin.models.domain import init_domain
        from redmin.models.choice import init_choices
        type_map = init_domain()
        init_fields(type_map)
        init_choices()
