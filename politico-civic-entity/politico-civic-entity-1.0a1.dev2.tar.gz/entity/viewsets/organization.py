# Imports from entity.
from entity.models import Organization
from entity.serializers import OrganizationSerializer
from entity.viewsets.base import BaseViewSet


class OrganizationViewSet(BaseViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
