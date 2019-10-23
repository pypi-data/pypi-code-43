# Imports from other dependencies.
from civic_utils.serializers import CommandLineListSerializer
from civic_utils.serializers import NaturalKeySerializerMixin
from geography.models import Division
from rest_framework import serializers
import us


class DistrictSerializer(NaturalKeySerializerMixin, CommandLineListSerializer):
    id = serializers.SerializerMethodField()

    def get_id(self, obj):
        return "{}-{}".format(obj.parent.code, obj.code)

    class Meta(CommandLineListSerializer.Meta):
        model = Division
        fields = ("label", "id")


class StateSerializer(NaturalKeySerializerMixin, CommandLineListSerializer):
    id = serializers.SerializerMethodField()
    postal_code = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.code

    def get_postal_code(self, obj):
        return us.states.lookup(obj.code).abbr

    class Meta(CommandLineListSerializer.Meta):
        model = Division
        fields = ("label", "id", "postal_code")
