import logging
from urllib.parse import unquote

from django.apps import apps
from django.conf import settings as django_settings

from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from dj_field_filemanager import settings
from dj_field_filemanager.serializers import create_serializer

logger = logging.getLogger(__name__)


class ModelViewSet(ViewSet):
    serializer_class = None
    parser_classes = (MultiPartParser,)
    permission_classes = settings.FIELD_FILEMANAGER_API_PERMISSIONS
    authentication_classes = (SessionAuthentication,)

    def get_model_class(self, model):
        app_label, model_name = model.split('.')
        return apps.get_model(app_label=app_label, model_name=model_name)

    def dispatch(self, request, model, parent_field, parent_pk, *args, **kwargs):
        model_class = self.get_model_class(model)
        self.model = model_class
        self.parent_field = parent_field
        self.parent_pk = parent_pk
        response = super().dispatch(request, *args, **kwargs)
        return response

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        fields = []
        for i in self.model._meta.get_fields():
            # if i.name != self.parent_field:
            fields.append(i.name)
        read_only_fields = ('thumbnail',)
        return create_serializer(self.model, fields, read_only_fields)

    def get_queryset(self):
        filter = {}
        filter[self.parent_field] = self.parent_pk
        qs = self.model.objects.filter(**filter)
        return qs

    def create(self, request):
        data = request.data
        if 'name' not in data:
            data['name'] = data['file'].name
        data[self.parent_field] = self.parent_pk
        serializer = None
        qs = self.get_queryset()
        document = qs.filter(name=data['name']).first()
        if document:
            serializer = self.get_serializer(
                document, data=request.data, context={'request': request})
        else:
            serializer = self.get_serializer(
                data=request.data, context={'request': request})
        if serializer.is_valid():
            instance = None
            try:
                instance = serializer.save()
            except Exception:
                if django_settings.DEBUG:
                    raise
            if instance:
                try:
                    instance.save_thumbnail()
                except Exception as e:
                    if django_settings.DEBUG:
                        raise
                    else:
                        logger.warning(e)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        items = self.get_queryset()
        serializer = self.get_serializer(items, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk, *args, **kwargs):
        pk = unquote(pk)
        item = self.get_queryset().get(name=pk)
        serializer = self.get_serializer(item, context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, pk, *args, **kwargs):
        item = self.get_queryset().get(name=pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
