# Imports from other dependencies.
from civic_utils.serializers import CommandLineListSerializer
from civic_utils.serializers import NaturalKeySerializerMixin
from election.models import Race
from geography.models import DivisionLevel
from rest_framework import serializers


# Imports from race_ratings.
from raceratings.models import RaceRating
from raceratings.serializers.category import CategorySerializer


class RaceRatingSerializer(
    NaturalKeySerializerMixin, CommandLineListSerializer
):
    category = serializers.SerializerMethodField()

    def get_category(self, obj):
        return CategorySerializer(obj.category).data

    class Meta(CommandLineListSerializer.Meta):
        model = RaceRating
        fields = ("pk", "created", "category", "explanation")


class RaceRatingAdminSerializer(CommandLineListSerializer):
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        return obj.category.short_label

    class Meta(CommandLineListSerializer.Meta):
        model = RaceRating
        fields = ("pk", "created", "rating", "explanation")


class RaceFeedSerializer(NaturalKeySerializerMixin, CommandLineListSerializer):
    label = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    body = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()

    def get_label(self, obj):
        if obj.office.body and obj.office.body.slug == "senate":
            label = "{} {}".format(obj.office.division.label, "Senate")
        else:
            label = obj.office.label

        if obj.special:
            return "{} Special".format(label)
        else:
            return label

    def get_id(self, obj):
        # for easier search
        if obj.office.division.level.slug == DivisionLevel.DISTRICT:
            postal = obj.office.division.parent.code_components["postal"]
            code = int(obj.office.division.code)
            return "{}-{}".format(postal, code)
        else:
            postal = obj.office.division.code_components["postal"]

            if obj.office.body:
                return "{}-{}".format(postal, "sen")
            else:
                return "{}-{}".format(postal, "gov")

    def get_body(self, obj):
        if obj.office.body:
            return obj.office.body.slug
        else:
            return "governor"

    def get_state(self, obj):
        if obj.office.division.level.name == DivisionLevel.DISTRICT:
            return obj.office.division.parent.code
        else:
            return obj.office.division.code

    def get_district(self, obj):
        if obj.office.division.level.name == DivisionLevel.DISTRICT:
            return "{}-{}".format(
                obj.office.division.parent.code, obj.office.division.code
            )
        else:
            return None

    class Meta(CommandLineListSerializer.Meta):
        model = Race
        fields = ("label", "id", "body", "state", "district")


class RaceRatingFeedSerializer(
    NaturalKeySerializerMixin, CommandLineListSerializer
):
    category = serializers.SerializerMethodField()
    race = serializers.SerializerMethodField()
    previous_category = serializers.SerializerMethodField()

    def get_category(self, obj):
        return CategorySerializer(obj.category).data

    def get_race(self, obj):
        return RaceFeedSerializer(obj.race).data

    def get_previous_category(self, obj):
        ordered_ratings = list(obj.race.ratings.order_by("created"))
        index = ordered_ratings.index(obj)
        return CategorySerializer(ordered_ratings[index - 1].category).data

    class Meta(CommandLineListSerializer.Meta):
        model = RaceRating
        fields = ("category", "race", "explanation", "previous_category")
