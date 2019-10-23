# Imports from other dependencies.
from civic_utils.serializers import CommandLineListSerializer
from civic_utils.serializers import NaturalKeySerializerMixin


# Imports from entity.
from entity.models import ImageTag


class ImageTagSerializer(NaturalKeySerializerMixin, CommandLineListSerializer):
    class Meta(CommandLineListSerializer.Meta):
        model = ImageTag
        fields = ("created", "updated")
