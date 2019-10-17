from .base import BaseViewSet


class UserViewSet(BaseViewSet):
    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset
