import logging

from rest_framework import serializers

from redmin.utils import import_class, attr

logger = logging.getLogger(__name__)


class BaseSerializer(serializers.ModelSerializer):
    def build_relational_field(self, field_name, relation_info):
        result = super().build_relational_field(field_name, relation_info)
        field_kwargs = result[1]
        # field_kwargs['queryset'] = filter_by_user(field_kwargs.pop("queryset"), attr(self, "context.request.user"))
        return result


def load_serializer_class(model):
    app = model.__module__.split(".")[0]
    name = f"{model.__name__}Serializer"
    try:
        clazz = import_class(f'{app}.rest.serializer.{name}')
        logger.info(f"load rest serializer:{clazz}")
        return clazz
    except (AttributeError, ModuleNotFoundError):
        model_fields = attr(model, '_meta.fields')
        all_fields = (set(attr(model, "form_fields", [])) | set(attr(model, "list_fields", []))) or set(
            [f.name for f in model_fields])
        excludes = set(attr(model, "form_exclude", [])) & set(attr(model, "list_exclude", []))
        fields = list(all_fields - excludes)
        return get_dynamic_serializer_class(model, fields)


def get_dynamic_serializer_class(model, fields):
    name = f"Dynamic{model.__name__}Serializer"
    return type(name, (BaseSerializer,), dict(
        Meta=type("Meta", (), dict(
            model=model,
            fields=fields,
            __module__=f"{__name__}.{name}"
        )),
        __module__=__name__
    ))
