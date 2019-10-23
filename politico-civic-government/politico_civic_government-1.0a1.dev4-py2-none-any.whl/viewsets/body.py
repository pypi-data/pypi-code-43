# Imports from government.
from government.models import Body
from government.serializers import BodySerializer
from government.viewsets.base import BaseViewSet


class BodyViewSet(BaseViewSet):
    queryset = Body.objects.all()
    serializer_class = BodySerializer
