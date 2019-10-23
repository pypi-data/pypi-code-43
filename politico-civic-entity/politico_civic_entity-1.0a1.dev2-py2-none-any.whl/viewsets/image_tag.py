# Imports from entity.
from entity.models import ImageTag
from entity.serializers import ImageTagSerializer
from entity.viewsets.base import BaseViewSet


class ImageTagViewSet(BaseViewSet):
    queryset = ImageTag.objects.all()
    serializer_class = ImageTagSerializer
