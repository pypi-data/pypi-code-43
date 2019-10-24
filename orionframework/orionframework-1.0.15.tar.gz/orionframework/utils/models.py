from orionframework.utils import lists


def clone(model):
    new_kwargs = dict(
        [(fld.name, getattr(model, fld.name)) for fld in model._meta.fields if fld.name != model._meta.pk])

    return get_model_class(model)(**new_kwargs)


def get_model_class(model):
    return model.__class__


def get_field(clazz, name):
    for field in clazz._meta.fields:
        if field.name == name:
            return field

    return None


def set_attrs(object, map):
    for key, value in map.items():
        setattr(object, key, value)

    return object


def get_choice_label(choices, choice):
    for entry in choices:

        if entry[0] == choice:
            return entry[1]

    return ""


def get_choice_id(tuples, str_value):
    if str_value:
        s = str_value.lower()
        for t in tuples:
            if t[1].lower() == s:
                return t[0]
    return None


def exists(record):
    clazz = get_model_class(record)
    pk = get_field(clazz, 'id')

    if pk.auto_created:
        return record.pk is not None

    return clazz.objects.filter(pk=record.pk).exists()


def diff_list(old_value, new_value):
    old_value = lists.as_list(old_value)
    new_value = lists.as_list(new_value)

    added = []
    removed = []

    for item in new_value:
        if item not in old_value:
            added.append(item)

    for item in old_value:
        if item not in new_value:
            removed.append(new_value)

    return {
        "added": added,
        "removed": removed
    }
