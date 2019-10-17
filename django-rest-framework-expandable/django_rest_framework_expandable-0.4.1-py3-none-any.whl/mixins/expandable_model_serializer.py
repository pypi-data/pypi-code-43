from django.db.models import Manager
from rest_framework.relations import ManyRelatedField

from .expandable import ExpandableMixin
from .expandable_related_field import ExpandableRelatedFieldMixin
from rest_framework_helpers.mixins import RepresentationMixin


class ExpandableModelSerializerMixin(RepresentationMixin, ExpandableMixin):
    def __init__(self, *args, **kwargs):
        self.expanded_fields = kwargs.pop("expanded_fields", None)
        super().__init__(*args, **kwargs)
        self.initialize_expandable_fields()

    def initialize_expandable_fields(self):
        model_name = self.get_model_name()

        for field_name, field in self.expandable_fields:
            field.model_name = model_name
            field.model_serializer = self
            field.model_serializer_field_name = field_name
            field.allowed_prefix = "{}.{}.".format(model_name, field_name)
            field.allowed = list(set([field_name] + getattr(field, "allowed", [])))

    @property
    def expandable_fields(self):
        """
        Returns a list of all the fields that subclass ExpandableRelatedFieldMixin
        """
        fields = []

        for field_name, field in self.fields.items():
            target = (
                field.child_relation if isinstance(field, ManyRelatedField) else field
            )

            if isinstance(target, ExpandableRelatedFieldMixin):
                fields.append([field_name, target])

        return fields

    def is_expandable(self, field):
        """
        Returns True if the field is a subclass of the ExpandableRelatedFieldMixin
        """
        target = field.child_relation if isinstance(field, ManyRelatedField) else field

        for field_name, field in self.expandable_fields:
            if field == target:
                return True

        return False

    def get_matched_paths(self, expandable_field):
        matched = []

        for requested_path in self.requested_fields:
            if expandable_field.is_matching(requested_path):
                expandable_field.assert_is_allowed(requested_path)
                expandable_field.assert_is_specified(requested_path)
                matched.append(requested_path)

        return matched

    def to_representation_for_field(self, field, obj):
        """
        A function to customize what each field representation produces. Can be
        overwritten in sublclasses to add custom behavoir on a per-field basis.

        By default, if the field is an expandable field, it will check if it should be
        expanded, and do so if checks pass.
        """
        if isinstance(obj, Manager):
            obj = obj.all()

        if self.is_expandable(field):
            target = getattr(field, "child_relation", field)

            matched = self.get_matched_paths(target)
            if len(matched):
                return target.to_expanded_representation(obj, matched)

        return field.to_representation(obj)
