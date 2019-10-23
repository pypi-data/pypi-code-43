# Imports from entity.
from entity.models import OrganizationClassification
from entity.serializers import OrganizationClassificationSerializer
from entity.viewsets.base import BaseViewSet


class OrganizationClassificationViewSet(BaseViewSet):
    queryset = OrganizationClassification.objects.all()
    serializer_class = OrganizationClassificationSerializer
