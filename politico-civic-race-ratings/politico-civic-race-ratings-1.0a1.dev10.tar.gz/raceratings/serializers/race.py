# Imports from Django.
from django.core.exceptions import ObjectDoesNotExist


# Imports from other dependencies.
from civic_utils.serializers import CommandLineListSerializer
from civic_utils.serializers import NaturalKeySerializerMixin
from election.models import Race
from election.models import Election
from geography.models import DivisionLevel
from rest_framework.reverse import reverse
from rest_framework import serializers


# Imports from race_ratings.
from raceratings.models import RatingPageContent
from raceratings.serializers.candidate import CandidateSerializer
from raceratings.serializers.category import CategorySerializer
from raceratings.serializers.race_rating import RaceRatingAdminSerializer
from raceratings.serializers.race_rating import RaceRatingSerializer


class RaceListSerializer(NaturalKeySerializerMixin, CommandLineListSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse(
            "raceratings_api_race-detail",
            request=self.context["request"],
            kwargs={"pk": obj.pk},
        )

    class Meta(CommandLineListSerializer.Meta):
        model = Race
        fields = ("url", "uid", "label")


class RaceAPISerializer(CommandLineListSerializer):
    latest_rating = serializers.SerializerMethodField()
    candidates = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    body = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()

    def get_latest_rating(self, obj):
        try:
            latest = obj.ratings.all()[0]
            return CategorySerializer(latest.category).data
        except ObjectDoesNotExist:
            return None

    def get_candidates(self, obj):
        try:
            gnl_election_for_race = obj.elections.all()[0]

            return CandidateSerializer(
                [
                    _.candidate
                    for _ in gnl_election_for_race.candidate_elections.all()
                ],
                many=True,
            ).data
        except IndexError:
            return []

    def get_label(self, obj):
        if not obj.office.body:
            if obj.division:
                label = "{} [{} electoral vote(s)]".format(
                    obj.office.label, obj.division.label
                )
            else:
                label = obj.office.label
        else:
            if obj.office.body.slug == "senate":
                label = "{} Senate".format(obj.office.division.label)
            elif obj.office.body.slug == "house":
                label = "{}, District {}".format(
                    obj.office.division.parent.label,
                    obj.office.division.code
                    if not obj.office.division.code.endswith("00")
                    else "At-Large",
                )

        if obj.special:
            label = "{}, Special Election".format(label)

        return label

    def get_id(self, obj):
        # for easier search
        if obj.office.division.level.slug == DivisionLevel.DISTRICT:
            postal = obj.office.division.parent.code_components["postal"]
            code = obj.office.division.code
            return "{}-{}".format(postal, code)

        elif obj.office.division.level.slug == DivisionLevel.COUNTRY:
            if obj.division.level.slug == DivisionLevel.STATE:
                postal = obj.division.code_components["postal"]
                return "{}-{}".format(postal, "potus")

            postal = obj.division.parent.code_components["postal"]
            return "{}_{}-{}".format(postal, obj.division.code, "potus")

        postal = obj.office.division.code_components["postal"]

        if obj.office.body:
            base = "{}-{}".format(postal, "sen")

            return "{}-{}".format(base, "special") if obj.special else base

        return "{}-{}".format(postal, "gov")

    def get_body(self, obj):
        if obj.office.body:
            return obj.office.body.slug

        return (
            "president"
            if obj.office.division.level.slug == DivisionLevel.COUNTRY
            else "governor"
        )

    def get_state(self, obj):
        if obj.office.division.level.name == DivisionLevel.DISTRICT:
            return obj.office.division.parent.code
        elif obj.office.division.level.slug == DivisionLevel.COUNTRY:
            if obj.division.level.name == DivisionLevel.DISTRICT:
                return obj.division.parent.code
            return obj.division.code
        else:
            return obj.office.division.code

    def get_district(self, obj):
        if obj.office.division.level.name == DivisionLevel.DISTRICT:
            return "{}-{}".format(
                obj.office.division.parent.code, obj.office.division.code
            )
        elif obj.office.division.level.slug == DivisionLevel.COUNTRY:
            if obj.division.level.name == DivisionLevel.DISTRICT:
                return "{}-{}".format(
                    obj.division.parent.code, obj.division.code
                )

        return None

    class Meta(CommandLineListSerializer.Meta):
        model = Race
        fields = (
            "latest_rating",
            "candidates",
            "label",
            "id",
            "pk",
            "body",
            "state",
            "district",
            "description",
        )


class RaceSerializer(NaturalKeySerializerMixin, CommandLineListSerializer):
    ratings = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    office = serializers.SerializerMethodField()

    def get_ratings(self, obj):
        return RaceRatingSerializer(obj.ratings, many=True).data

    def get_content(self, obj):
        return RatingPageContent.objects.race_content(obj)

    def get_office(self, obj):
        if not obj.office.body:
            label = obj.office.label
        else:
            if obj.office.body.slug == "senate":
                label = "{} Senate".format(obj.office.division.label)
            elif obj.office.body.slug == "house":
                label = "{}, District {}".format(
                    obj.office.division.parent.label, obj.office.division.code
                )

        if obj.special:
            label = "{}, Special Election".format(label)

        return label

    class Meta(CommandLineListSerializer.Meta):
        model = Race
        fields = ("uid", "ratings", "content", "office")


class RaceAdminSerializer(CommandLineListSerializer):
    ratings = serializers.SerializerMethodField()
    office = serializers.SerializerMethodField()

    # a bunch of search fields
    abbrev = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()

    def get_ratings(self, obj):
        return RaceRatingAdminSerializer(obj.ratings.all(), many=True).data

    def get_office(self, obj):
        if obj.office.body and obj.office.body.slug == "senate":
            label = "{} {}".format(obj.office.division.label, "Senate")
        else:
            label = obj.office.label

        if obj.special:
            return "{} Special".format(label)
        else:
            return label

    def get_abbrev(self, obj):
        # for easier search
        if obj.office.division.level.slug == DivisionLevel.DISTRICT:
            postal = obj.office.division.parent.code_components["postal"]
            code = int(obj.office.division.code)
            return "{}-{}".format(postal, code)
        elif obj.office.division.level.slug == DivisionLevel.COUNTRY:
            if obj.division.level.slug == DivisionLevel.STATE:
                postal = obj.division.code_components["postal"]
                return "{}-{}".format(postal, "potus")
            else:
                postal = obj.division.parent.code_components["postal"]
                return "{}_{}-{}".format(postal, obj.division.code, "potus")
        else:
            postal = obj.office.division.code_components["postal"]

            if obj.office.body:
                return "{}-{}".format(postal, "sen")
            else:
                return "{}-{}".format(postal, "gov")

    def get_code(self, obj):
        if obj.office.division.level.slug == DivisionLevel.DISTRICT:
            return int(obj.office.division.code)
        else:
            return 0

    class Meta(CommandLineListSerializer.Meta):
        model = Race
        fields = ("uid", "ratings", "office", "abbrev", "code", "special")
