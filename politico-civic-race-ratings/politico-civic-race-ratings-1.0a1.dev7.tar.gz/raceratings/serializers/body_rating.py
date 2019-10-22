# Imports from other dependencies.
from civic_utils.serializers import CommandLineListSerializer
from civic_utils.serializers import NaturalKeySerializerMixin
from rest_framework import serializers


# Imports from race_ratings.
from raceratings.models import BodyRating
from raceratings.serializers.category import CategorySerializer


class BodyRatingSerializer(
    NaturalKeySerializerMixin, CommandLineListSerializer
):
    category = serializers.SerializerMethodField()
    body = serializers.SerializerMethodField()

    def get_category(self, obj):
        return CategorySerializer(obj.category).data

    def get_body(self, obj):
        return obj.body.slug

    class Meta(CommandLineListSerializer.Meta):
        model = BodyRating
        fields = ("created", "category", "explanation", "body")
