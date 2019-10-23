# Imports from other dependencies.
from civic_utils.serializers import CommandLineListSerializer
from civic_utils.serializers import NaturalKeySerializerMixin


# Imports from race_ratings.
from raceratings.models import Category


class CategorySerializer(CommandLineListSerializer):
    class Meta(CommandLineListSerializer.Meta):
        model = Category
        fields = ("id", "label", "short_label", "order")


class CategoryListSerializer(
    NaturalKeySerializerMixin, CommandLineListSerializer
):
    class Meta(CommandLineListSerializer.Meta):
        model = Category
        fields = ("id", "label", "short_label", "order")
