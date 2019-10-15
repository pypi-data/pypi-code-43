import io
import logging
import os
import uuid
from importlib import import_module

from django.conf import settings as django_settings
from django.core.files.base import ContentFile
from django.db import models
from django.utils.translation import ugettext_lazy as _

import pdf2image
from PIL import Image, ImageOps

from . import settings


logger = logging.getLogger(__name__)


def _thumbnail_upload_to(instance, filename):
    return instance.thumbnail_upload_to(filename)


def _upload_to(instance, filename):
    return instance.upload_to(filename)


class ThumbnailMixin:
    ALLOWED_IMAGE_FORMATS = ('JPEG', 'PNG')
    EXTENSIONS = {
        'JPEG': 'jpg',
        'PNG': 'png',
    }
    PNG_SUPPORTED_MODES = ('1', 'L', 'RGB', 'RGBA')
    width = None
    height = None

    def get_file_name(self):
        raise NotImplementedError()

    def get_thumbnail_height(self):
        return self.width or settings.FIELD_FILEMANAGER_HEIGHT

    def get_thumbnail_width(self):
        return self.height or settings.FIELD_FILEMANAGER_WIDTH

    def open_file(self):
        raise NotImplementedError()

    def _thumbnail_save(self):
        im = None
        format = None
        file = None
        if self.get_file_name().lower().endswith('.pdf'):
            file = self.open_file()
            images = pdf2image.convert_from_bytes(file.read(), first_page=1, last_page=1)
            if len(images) > 0:
                im = images[0]
                format = 'JPEG'
        else:
            try:
                file = self.open_file()
                im = Image.open(file)
                # Keep the same format if it's OK for us
                if im.format in self.ALLOWED_IMAGE_FORMATS:
                    format = im.format
                else:
                    # Convert it into PNG
                    if im.mode not in self.PNG_SUPPORTED_MODES:
                        # Force a valid PNG mode (RGB)
                        im = im.convert('RGBA')
                    format = 'PNG'
            except Exception as e:
                if django_settings.DEBUG:
                    logger.warning(e)
                im = None

        if im:
            # generate thumbnail
            try:
                im = ImageOps.exif_transpose(im)
            except Exception:
                pass
            size = (self.get_thumbnail_width(), self.get_thumbnail_height())
            im.thumbnail(size, Image.ANTIALIAS)
            buffer = io.BytesIO()
            im.save(buffer, format=format)

            buffer.seek(0)
            bytes = buffer.read()
            if file and not file.closed:
                file.close()
            if format in self.EXTENSIONS:
                extension = self.EXTENSIONS[format]
            else:
                extension = format.lower()

            return bytes, extension


class DocumentModel(models.Model, ThumbnailMixin):
    # Parent attribute name
    document_parent = None

    name = models.CharField(_('Name'), max_length=255, blank=True)
    file = models.FileField(_('File'), max_length=255, upload_to=_upload_to,
                            storage=settings.FIELD_FILEMANAGER_STORAGE())
    thumbnail = models.FileField(_('Thumbnail'), max_length=255, blank=True,
                                 null=True, upload_to=_thumbnail_upload_to,
                                 storage=settings.FIELD_FILEMANAGER_STORAGE())

    def get_file_name(self):
        if self.file:
            return self.file.name

    @classmethod
    def get_parent(cls):
        if cls.document_parent is None:
            raise Exception("'document_parent' ForeignKey field is not defined")
        return cls.document_parent

    def open_file(self):
        self.file.open()
        return self.file

    @classmethod
    def parent_base_upload_to(cls, parent):
        """
        Returns the desired the base path for parent_model.

        By default it's 'app_label/parent_model/parent_rel_id' where:
          - app_label is the parent's app label
          - parent_model is the model name of the parent model
          - parent_rel_id is the identity of the parent as it is on the foreign key (usually the pk)
        """
        return '%s/%s/%s' % (parent._meta.app_label, parent._meta.model_name, parent.pk)

    def base_upload_to(self):
        """
        Returns the desired the base path for current model.

        By default it's 'app_label/parent_model/parent_rel_id/current' where:
          - app_label is the parent's app label
          - parent_model is the model name of the parent model
          - parent_rel_id is the identity of the parent as it is on the foreign key (usually the pk)
          - current model name
        """
        parent = getattr(self, (self.get_parent()))
        remote = self._meta.get_field(self.get_parent()).remote_field.name
        return '%s/%s' % (self.parent_base_upload_to(parent), remote)

    @classmethod
    def check_delete_parent_folder(cls, parent):
        """
        Check if the parent folder hasn't files and can be deleted
        """
        folder = os.path.join(
            settings.MEDIA_ROOT, cls.parent_base_upload_to(parent))

        def rmdir(target):
            items = os.listdir(target)
            if len(items) == 0:
                os.rmdir(target)
            else:
                for item in items:
                    path = os.path.join(target, item)
                    if not os.path.isdir(path):
                        msg = 'The folder %s contains some file' % path
                        raise FolderNotEmptyException(msg)
                for item in items:
                    path = os.path.join(target, item)
                    rmdir(path)
                os.rmdir(target)

        try:
            rmdir(folder)
        except Exception as e:
            logger.warning(e)

    def deferred_post_delete(self):
        """
        Called from transaction.on_commit.
        """
        if self.file and os.path.isfile(self.file.path):
            self.file.delete(save=False)
        if self.thumbnail and os.path.isfile(self.thumbnail.path):
            self.thumbnail.delete(save=False)

    def save_thumbnail(self, save=True):
        """
        Generates a document thumbnail
        """
        modified = False
        if self.thumbnail:
            self.thumbnail.delete(save=False)
            modified = True

        result = self._thumbnail_save()
        if result:
            bytes, extension = result
            filename = '%s.%s' % (uuid.uuid4(), extension)
            self.thumbnail.save(name=filename, content=ContentFile(bytes))
            modified = True

        if modified and save:
            self.save()

    def thumbnail_upload_to(self, filename):
        """
        Returns then path for thumbnail image
        """
        base_path = self.base_upload_to()
        return '%s/%s/%s' % (base_path, 'filemanager_thumbnails', filename)

    def upload_to(self, filename):
        """
        Returns the path for document
        """
        base_path = self.base_upload_to()
        return '%s/%s/%s' % (base_path, 'filemanager', filename)

    class Meta:
        abstract = True


class FolderNotEmptyException(Exception):
    pass


class StorageFileModelBase(ThumbnailMixin):
    storage_config = None
    auto_thumbnail = False

    def __init__(self, name=None, file=None, thumbnail=None):
        self.name = name
        self.file = file
        self.thumbnail = thumbnail

    def get_file_name(self):
        return self.name

    @classmethod
    def get_object(cls, file_name):
        if cls.get_storage().exists(file_name):
            obj = cls()
            obj.name = file_name
            obj.file = file_name
            obj.thumbnail = cls.get_thumbnail(file_name)
            return obj

    def open_file(self):
        return self.get_storage().open(self.name)

    @classmethod
    def _get_storage(cls, config):
        storage_type = cls.get_storage_type()
        args = {}
        if storage_type == 'django.core.files.storage.FileSystemStorage':
            storage_type = 'dj_field_filemanager.storage.OverwriteStorage'
        if 'path' not in config:
            raise Exception('missing path attribute')
        args['location'] = config['path']
        if 'url' not in config:
            raise Exception('missing url attribute')
        args['base_url'] = config['url']
        if 'extra' in config:
            args.update(config['extra'])
        p, m = storage_type.rsplit('.', 1)
        mod = import_module(p)
        Storage = getattr(mod, m)
        storage = Storage(**args)
        return storage

    @classmethod
    def get_storage(cls):
        return cls._get_storage(cls.storage_config)

    @classmethod
    def get_storage_type(cls):
        config = cls.storage_config
        if 'storage' in config:
            type_ = config['storage']
        else:
            type_ = settings.FIELD_FILEMANAGER_STORAGE_DEFAULT_STORAGE
        return type_

    @classmethod
    def get_thumbnail(cls, file_name):
        if cls.get_storage().exists(file_name):
            extensions = list(cls.EXTENSIONS.values())
            storage_thumbnail = cls.get_thumbnail_storage()
            for e in extensions:
                thumbnail_name = '%s.thumbnail.%s' % (file_name, e)
                if storage_thumbnail.exists(thumbnail_name):
                    return storage_thumbnail.path(thumbnail_name)

    def get_thumbnail_height(self):
        if 'height' in self.storage_config['thumbnail']:
            return self.storage_config['thumbnail']['height']
        return settings.FIELD_FILEMANAGER_HEIGHT

    def get_thumbnail_width(self):
        if 'width' in self.storage_config['thumbnail']:
            return self.storage_config['thumbnail']['width']
        return settings.FIELD_FILEMANAGER_WIDTH

    @classmethod
    def get_thumbnail_storage(cls):
        if 'thumbnail' not in cls.storage_config:
            return None
        return cls._get_storage(cls.storage_config['thumbnail'])

    def refresh(self):
        self.file = None
        self.thumbnail = None
        if self.get_storage().exists(self.name):
            # self.name is set on save
            self.file = self.name
            self.thumbnail = self.get_thumbnail(self.name)

    def save(self, data):
        self.name = self.get_storage().save(data['name'], data['file'])
        self.refresh()
        if self.auto_thumbnail:
            try:
                self.save_thumbnail()
            except Exception as e:
                if django_settings.DEBUG:
                    raise
                else:
                    logger.warning(e)

    def save_thumbnail(self):
        """
        Generates a thumbnail
        """
        storage_thumbnail = self.get_thumbnail_storage()
        if self.thumbnail:
            if storage_thumbnail.exists(self.thumbnail):
                storage_thumbnail.delete(self.thumbnail)

        result = self._thumbnail_save()
        if result:
            bytes, extension = result
            filename = '%s.thumbnail.%s' % (self.get_file_name(), extension)
            self.thumbnail = storage_thumbnail.save(
                name=filename, content=ContentFile(bytes))

    @property
    def version(self):
        modified = -1
        try:
            modified = self.get_storage().get_modified_time(self.file)
        except Exception:
            pass
        return modified


def create_storage_file_model(storage_config, auto_thumbnail=False):
    attrs = {
        '__module__': 'dj_field_filemanager',
        'storage_config': storage_config,
        'auto_thumbnail': auto_thumbnail
    }
    model = type(str('StorageFileModel%s') % str(
        storage_config['code']).capitalize, (StorageFileModelBase,), attrs)
    return model
