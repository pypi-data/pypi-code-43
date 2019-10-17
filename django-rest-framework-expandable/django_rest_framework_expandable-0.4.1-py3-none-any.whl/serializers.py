from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer
from .mixins.expandable_model_serializer import ExpandableModelSerializerMixin


class ExpandableHyperlinkedModelSerializer(
    ExpandableModelSerializerMixin, HyperlinkedModelSerializer
):
    pass


class ExpandableModelSerializer(ExpandableModelSerializerMixin, ModelSerializer):
    pass
