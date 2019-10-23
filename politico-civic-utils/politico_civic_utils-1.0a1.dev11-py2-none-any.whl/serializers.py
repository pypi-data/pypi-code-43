# Imports from python.
from collections import OrderedDict
from io import StringIO


# Imports from Django.
from django.core.serializers.base import DeserializedObject
from django.core.serializers.base import ProgressBar
from django.db import models
from django.utils.functional import cached_property


# Imports from other dependencies.
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.utils import model_meta
from rest_framework.validators import UniqueValidator


# Imports from civic_utils.
from civic_utils.models import CivicBaseModel


class CommandLineSerializerMixin(object):
    def serialize_to_cli(
        self,
        data=None,
        stream=None,
        progress_output=None,
        object_count=0,
        renderer=None,
        **options,
    ):
        if data is None:
            data = self.instance

        self.cli_options = options
        self.cli_stream = stream if stream is not None else StringIO()
        progress_bar = ProgressBar(progress_output, object_count)

        self.start_cli_serialization()
        self.cli_first_item = True
        self.cli_renderer_klass = renderer or JSONRenderer

        iterable = data.all() if isinstance(data, models.Manager) else data

        for count, obj in enumerate(iterable, start=1):
            self.start_object(obj)
            self.end_object(obj)

            progress_bar.update(count)

            self.cli_first_item = self.cli_first_item and False

        self.end_cli_serialization()
        return self.getvalue()

    def start_cli_serialization(self):
        self._current = None
        self.cli_exported_objects = []

    def end_cli_serialization(self):
        renderer_context = {}

        if "indent" in self.cli_options:
            renderer_context["indent"] = self.cli_options["indent"]

        self.cli_stream.write(
            self.cli_renderer_klass()
            .render(
                self.cli_exported_objects, renderer_context=renderer_context
            )
            .decode("utf-8")
        )

    def start_object(self, obj):
        self._current = self.child.to_representation(obj)

    def end_object(self, obj):
        self.cli_exported_objects.append(self._current)
        self._current = None

    def getvalue(self):
        """
        Return the fully serialized queryset (or None if the output stream is
        not seekable).
        """
        if callable(getattr(self.cli_stream, "getvalue", None)):
            return self.cli_stream.getvalue()


class CommandLineDeserializerMixin(object):
    def to_python(self, raw_data):
        if hasattr(self, "many") and self.many:
            return [self.child.to_python(instance) for instance in raw_data]

        model_klass = self.Meta.model

        info = model_meta.get_field_info(model_klass)

        m2m_naturalkeys = {}
        deferred_fields = {}

        for field_name, relation_info in info.relations.items():
            if relation_info.reverse is True:
                continue

            if not issubclass(relation_info.related_model, CivicBaseModel):
                continue

            relationship_name = relation_info.model_field.name

            related_nk_fields = relation_info.related_model.natural_key_fields

            relation_natural_key_fields = [
                f"{relationship_name}__{natural_key_component}"
                for natural_key_component in related_nk_fields
            ]

            if not all(
                [field in raw_data for field in relation_natural_key_fields]
            ):
                raise ValueError(
                    "Missing one or more fields needed to construct the "
                    f"natural key for '{relationship_name}'."
                )

            current_natural_key = [
                raw_data.pop(field) for field in relation_natural_key_fields
            ]

            if relation_info.to_many:
                m2m_naturalkeys[relationship_name] = current_natural_key
            else:
                deferred_fields[relationship_name] = current_natural_key

        return DeserializedObject(
            model_klass(**raw_data), m2m_naturalkeys, deferred_fields
        )

    def deserialize(self, initial_data):
        self.initial_data = initial_data

        if not self.is_valid():
            raise ValueError(self.errors)

        return self.to_python(self.validated_data)


class CommandLineCapableListSerializer(
    CommandLineSerializerMixin,
    CommandLineDeserializerMixin,
    serializers.ListSerializer,
):
    pass


class CommandLineListSerializer(
    CommandLineDeserializerMixin, serializers.ModelSerializer
):
    created = serializers.DateTimeField(format="iso-8601")
    updated = serializers.DateTimeField(format="iso-8601")

    class Meta:
        list_serializer_class = CommandLineCapableListSerializer


class NaturalKeyValidator(serializers.UniqueTogetherValidator):
    def set_context(self, serializer):
        self.nested_fields = {
            name: serializer.fields[name]
            for name in self.fields
            if isinstance(serializer.fields[name], NaturalKeySerializer)
        }
        super(NaturalKeyValidator, self).set_context(serializer)

    def filter_queryset(self, attrs, queryset):
        attrs = attrs.copy()
        for field in attrs:
            if field in self.nested_fields:
                assert isinstance(attrs[field], dict)
                cls = self.nested_fields[field].Meta.model
                result = cls._default_manager.filter(**attrs[field])
                if result.count() == 0:
                    # No existing nested object for these values
                    return queryset.none()
                else:
                    # Existing nested object, use it to validate
                    attrs[field] = result[0].pk

        return super(NaturalKeyValidator, self).filter_queryset(
            attrs, queryset
        )


class NaturalKeySerializer(serializers.ModelSerializer):
    """Self-nesting serializer for natural-keyed models."""

    def build_standard_field(self, field_name, model_field):
        field_class, field_kwargs = super(
            NaturalKeySerializer, self
        ).build_standard_field(field_name, model_field)

        if "validators" in field_kwargs:
            field_kwargs["validators"] = [
                validator
                for validator in field_kwargs.get("validators", [])
                if not isinstance(validator, UniqueValidator)
            ]
        return field_class, field_kwargs

    def build_nested_field(self, field_name, relation_info, nested_depth):
        field_class = NaturalKeySerializer.for_model(
            relation_info.related_model, validate_key=False
        )
        field_kwargs = {}
        return field_class, field_kwargs

    # def create(self, validated_data):
    #     model_class = self.Meta.model
    #     natural_key_fields = model_class.get_natural_key_fields()
    #     natural_key = []
    #     for field in natural_key_fields:
    #         val = validated_data
    #         for key in field.split('__'):
    #             val = val[key]
    #         natural_key.append(val)
    #     return model_class.objects.find(*natural_key)
    #
    # def update(self, instance, validated_data):
    #     raise NotImplementedError(
    #         "Updating an existing natural key is not supported."
    #     )

    @classmethod
    def for_model(cls, model_class, validate_key=True, include_fields=None):
        unique_together = model_class.get_natural_key_definition()
        if include_fields and list(include_fields) != list(unique_together):
            raise NotImplementedError(
                "NaturalKeySerializer for '%s' has unique_together = [%s], "
                "but provided include_fields = [%s]"
                % (
                    model_class._meta.model_name,
                    ", ".join(unique_together),
                    ", ".join(include_fields),
                )
            )

        class Serializer(cls):
            class Meta(cls.Meta):
                model = model_class
                fields = unique_together
                if validate_key:
                    validators = [
                        NaturalKeyValidator(
                            queryset=model_class._default_manager,
                            fields=unique_together,
                        )
                    ]
                else:
                    validators = []

        return Serializer

    @classmethod
    def for_depth(cls, model_class):
        return cls

    class Meta:
        depth = 1


class NaturalKeySerializerMixin(object):
    """Natural key support across related models.

    Properly serializes models that have one or more foreign keys to
    natural-keyed model(s).
    """

    pk = serializers.SerializerMethodField(method_name="get_natural_key")

    @cached_property
    def fields(self):
        raw_fields = super(NaturalKeySerializerMixin, self).fields

        # Add the 'pk' field to output.
        raw_fields["pk"] = self.pk

        # Make 'pk' the first field displayed.
        raw_fields.fields.move_to_end("pk", last=False)

        return raw_fields

    def get_natural_key(self, obj):
        return obj.natural_key()

    def build_nested_field(self, field_name, relation_info, nested_depth):
        if issubclass(relation_info.related_model, CivicBaseModel):
            field_class = NaturalKeySerializer.for_model(
                relation_info.related_model, validate_key=False
            )

            field_kwargs = {}
            if relation_info.model_field is not None:
                if relation_info.model_field.null:
                    field_kwargs["required"] = False
            return field_class, field_kwargs

        return super(NaturalKeySerializerMixin, self).build_nested_field(
            field_name, relation_info, nested_depth
        )

    def build_relational_field(self, field_name, relation_info):
        field_class, field_kwargs = super(
            NaturalKeySerializerMixin, self
        ).build_relational_field(field_name, relation_info)
        if issubclass(relation_info.related_model, CivicBaseModel):
            field_kwargs.pop("queryset")
            field_kwargs["read_only"] = True
        return field_class, field_kwargs

    def get_fields(self):
        fields = super(NaturalKeySerializerMixin, self).get_fields()
        fields.update(self.build_natural_key_fields(fields))
        return fields

    def build_natural_key_fields(self, raw_fields):
        info = model_meta.get_field_info(self.Meta.model)
        fields = OrderedDict()
        for field, relation_info in info.relations.items():
            if not issubclass(relation_info.related_model, CivicBaseModel):
                continue

            if field in raw_fields and not isinstance(
                raw_fields[field], serializers.SerializerMethodField
            ):
                field_class, field_kwargs = self.build_nested_field(
                    field, relation_info, 1
                )
                fields[field] = field_class(**field_kwargs)
        return fields

    # def create(self, validated_data):
    #     self.convert_natural_keys(
    #         validated_data
    #     )
    #     return super(NaturalKeySerializerMixin, self).create(
    #         validated_data
    #     )
    #
    # def update(self, instance, validated_data):
    #     self.convert_natural_keys(
    #         validated_data
    #     )
    #     return super(NaturalKeySerializerMixin, self).update(
    #         instance, validated_data
    #     )
    #
    # def convert_natural_keys(self, validated_data):
    #     fields = self.get_fields()
    #     for name, field in fields.items():
    #         if name not in validated_data:
    #             continue
    #         if isinstance(field, NaturalKeySerializer):
    #             validated_data[name] = fields[name].create(
    #                 validated_data[name]
    #             )

    @classmethod
    def for_model(cls, model_class, include_fields=None):
        # c.f. wq.db.rest.serializers.ModelSerializer
        class Serializer(cls):
            class Meta(cls.Meta):
                model = model_class
                if include_fields:
                    fields = include_fields

        return Serializer

    def get_unique_constraint_fields(self):
        return [
            field.name
            for field in self.Meta.model._meta.get_fields()
            if hasattr(field, "unique") and field.unique
        ]

    def run_validation(self, data):
        raw_natural_key_fields = data.pop("pk")

        cached_unique_fields = {}
        unique_fields = self.get_unique_constraint_fields()
        for field in unique_fields:
            if field in data:
                cached_unique_fields[field] = data[field]

        natural_key_components = dict(
            zip(
                self.Meta.model.get_natural_key_fields(),
                raw_natural_key_fields,
            )
        )

        validated = super(NaturalKeySerializerMixin, self).run_validation(data)

        validated.update(natural_key_components)

        for field_name, cached_value in cached_unique_fields.items():
            if field_name not in validated:
                validated.update(dict([(field_name, cached_value)]))

        return validated

    class Meta:
        pass
