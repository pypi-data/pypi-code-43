from rest_framework.serializers import SlugRelatedField, HyperlinkedRelatedField
from .mixins.expandable_related_field import ExpandableRelatedFieldMixin


class ExpandableHyperlinkedRelatedField(
    ExpandableRelatedFieldMixin, HyperlinkedRelatedField
):
    pass


class ExpandableSlugRelatedField(ExpandableRelatedFieldMixin, SlugRelatedField):
    pass
