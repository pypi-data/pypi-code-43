# Imports from government.
from government.models import Jurisdiction
from government.serializers import JurisdictionSerializer
from government.viewsets.base import BaseViewSet


class JurisdictionViewSet(BaseViewSet):
    queryset = Jurisdiction.objects.all()
    serializer_class = JurisdictionSerializer
