from rest_framework import viewsets, mixins
from rest_framework.decorators import action

from rest_framework.response import Response

from ..models import UserGenericTypeformFeedback
from .serializers import (
    UserResponseValidationSerializer,
    UserResponseOKSerializer,
    UserResponseKOSerializer,
)


class UserTypeformViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):

    queryset = UserGenericTypeformFeedback.objects.all()
    lookup_field = 'uuid'
    serializers = {
        'default': UserResponseValidationSerializer,
        'validate': UserResponseOKSerializer,
        'invalidate': UserResponseKOSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers['default'])

    @action(detail=True, methods=['post'], url_path='validate')
    def validate(self, request, uuid):
        serializer = self.get_serializer_class()(
            data={'uuid': uuid},
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(self.get_object(), {})

        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='invalidate')
    def invalidate(self, request, uuid):
        serializer = self.get_serializer_class()(
            data={'uuid': uuid},
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(self.get_object(), {})

        return Response(serializer.data)
