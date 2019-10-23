# Imports from other dependencies.
from civic_utils.serializers import CommandLineListSerializer
from civic_utils.serializers import NaturalKeySerializerMixin
from rest_framework import serializers


# Imports from entity.
from entity.models import Person


class PersonSerializer(NaturalKeySerializerMixin, CommandLineListSerializer):
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        """Object of images serialized by tag name."""
        return {str(i.tag.name): i.image for i in obj.images.all()}

    class Meta(CommandLineListSerializer.Meta):
        model = Person
        fields = (
            "slug",
            "last_name",
            "first_name",
            "middle_name",
            "suffix",
            "full_name",
            "identifiers",
            "gender",
            "race",
            "nationality",
            "state_of_residence",
            "birth_date",
            "death_date",
            "images",
            "summary",
            "description",
            "links",
            "created",
            "updated",
        )
