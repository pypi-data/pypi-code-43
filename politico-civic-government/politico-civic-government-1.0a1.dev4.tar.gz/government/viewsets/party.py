# Imports from government.
from government.models import Party
from government.serializers import PartySerializer
from government.viewsets.base import BaseViewSet


class PartyViewSet(BaseViewSet):
    queryset = Party.objects.all()
    serializer_class = PartySerializer
