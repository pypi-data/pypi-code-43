# Imports from other dependencies.
from civic_utils.serializers import CommandLineListSerializer
from civic_utils.serializers import NaturalKeySerializerMixin


# Imports from government.
from government.models import Party


class PartySerializer(NaturalKeySerializerMixin, CommandLineListSerializer):
    class Meta(CommandLineListSerializer.Meta):
        model = Party
        fields = "__all__"
