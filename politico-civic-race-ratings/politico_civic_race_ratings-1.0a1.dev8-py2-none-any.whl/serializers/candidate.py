# Imports from other dependencies.
from civic_utils.serializers import CommandLineListSerializer
from civic_utils.serializers import NaturalKeySerializerMixin
from election.models import Candidate
from rest_framework import serializers


class CandidateSerializer(
    # NaturalKeySerializerMixin
    CommandLineListSerializer
):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    party = serializers.SerializerMethodField()

    def get_first_name(self, obj):
        return obj.person.first_name

    def get_last_name(self, obj):
        return obj.person.last_name

    def get_party(self, obj):
        return obj.party.label

    class Meta(CommandLineListSerializer.Meta):
        model = Candidate
        fields = ("first_name", "last_name", "party", "incumbent")
