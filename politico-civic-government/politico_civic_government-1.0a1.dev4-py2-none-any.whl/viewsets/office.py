# Imports from government.
from government.models import Office
from government.serializers import OfficeSerializer
from government.viewsets.base import BaseViewSet


class OfficeViewSet(BaseViewSet):
    queryset = Office.objects.all()
    serializer_class = OfficeSerializer
