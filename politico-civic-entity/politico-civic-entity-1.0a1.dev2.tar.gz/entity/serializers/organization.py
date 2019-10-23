# Imports from other dependencies.
from civic_utils.serializers import CommandLineListSerializer
from civic_utils.serializers import NaturalKeySerializerMixin
from rest_framework import serializers


# Imports from entity.
from entity.models import Organization


class OrganizationSerializer(
    NaturalKeySerializerMixin, CommandLineListSerializer
):
    images = serializers.SerializerMethodField()
    classification = serializers.StringRelatedField()

    def get_images(self, obj):
        """Object of images serialized by tag name."""
        return {str(i.tag.name): i.image for i in obj.images.all()}

    class Meta(CommandLineListSerializer.Meta):
        model = Organization
        fields = (
            "id",
            "uid",
            "slug",
            "name",
            "identifiers",
            "classification",
            "parent",
            "national_headquarters",
            "founding_date",
            "dissolution_date",
            "images",
            "summary",
            "description",
            "links",
            "created",
            "updated",
        )
