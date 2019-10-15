import logging
import os

from django.conf import settings as django_settings

from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from dj_field_filemanager import settings
from dj_field_filemanager.models import create_storage_file_model
from dj_field_filemanager.serializers import StorageSerializer

logger = logging.getLogger(__name__)


class StorageViewSet(ViewSet):
    serializer_class = StorageSerializer
    parser_classes = (MultiPartParser,)
    permission_classes = settings.FIELD_FILEMANAGER_STORAGE_PERMISSIONS
    authentication_classes = (SessionAuthentication,)

    def create(self, request):
        storage = self.model.get_storage()
        data = request.data
        if 'name' not in data:
            data['name'] = data['file'].name
        data['name'] = storage.get_valid_name(os.path.basename(data['name']))
        serializer = None

        if storage.exists(data['name']):
            instance = self.model.get_object(data['name'])
            serializer = self.get_serializer(
                instance, data=request.data, context={'request': request},
                model=self.model)
        else:
            serializer = self.get_serializer(
                data=request.data, context={'request': request}, model=self.model)

        if serializer.is_valid():
            instance = None
            try:
                serializer.save()
            except Exception:
                if django_settings.DEBUG:
                    raise
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def dispatch(self, request, code, *args, **kwargs):
        storage_config = self.get_storage_config(code)
        if storage_config is None:
            raise Exception('Folder configuration not found for [%s]' % code)
        self.model = create_storage_file_model(storage_config)
        self.model.auto_thumbnail = 'thumbnail' in storage_config
        response = super().dispatch(request, *args, **kwargs)
        return response

    def get_files(self, storage):
        dirs = []
        files = []
        try:
            dirs, files = storage.listdir('.')
        except Exception as e:
            if django_settings.DEBUG:
                logger.warning(e)
        return files

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['model'] = self.model
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        return self.serializer_class

    def get_storage_config(self, code):
        if not hasattr(self, '_storage_config'):
            self.storage_config = None
            for item in settings.FIELD_FILEMANAGER_STORAGE_CONFIG:
                if item['code'] == code:
                    self.storage_config = item
                    break
        return self.storage_config

    def list(self, request, *args, **kwargs):
        storage = self.model.get_storage()
        thumbnail_storage = self.model.get_thumbnail_storage()

        files = self.get_files(storage)
        thumbnails_ = self.get_files(thumbnail_storage)
        thumbnails = {}
        for thumbnail in thumbnails_:
            filename = thumbnail.split('.thumbnail.')[0]
            thumbnails[filename] = thumbnail
        items = []
        for f in sorted(files):
            # ignore empty names
            if not f:
                continue
            thumbnail = None
            if f in thumbnails:
                thumbnail = thumbnails[f]
            items.append(self.model(**{
                'name': f,
                'file': f,
                'thumbnail': thumbnail,
            }))
        serializer = self.get_serializer(
            items, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk, *args, **kwargs):
        obj = self.model.get_object(os.path.basename(pk))
        if not obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(
            obj, context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, pk, *args, **kwargs):
        obj = self.model.get_object(os.path.basename(pk))
        if obj:
            if obj.thumbnail:
                self.model.get_thumbnail_storage().delete(obj.thumbnail)
            if self.model.get_storage().exists(obj.file):
                self.model.get_storage().delete(obj.file)
        return Response(status=status.HTTP_204_NO_CONTENT)
