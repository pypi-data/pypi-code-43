from django.conf import settings
from django.utils.module_loading import import_string

from .permissions import ModelHasPermission, StorageHasPermission
from .storage import OverwriteStorage


def get_cls(key, default):
    value = getattr(settings, key, None)
    if type(value) is type:
        return value
    elif type(value) is tuple or type(value) is list:
        return tuple(import_string(p) for p in value if type(p) is str)
    elif type(value) is str:
        return import_string(value)
    else:
        return default


FIELD_FILEMANAGER_WIDTH = getattr(settings, 'FIELD_FILEMANAGER_WIDTH', 240)
FIELD_FILEMANAGER_HEIGHT = getattr(settings, 'FIELD_FILEMANAGER_HEIGHT', 240)
MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')

FIELD_FILEMANAGER_USE_VUE_JS = getattr(settings, 'FIELD_FILEMANAGER_USE_VUE_JS', True)

FIELD_FILEMANAGER_STORAGE = get_cls('FIELD_FILEMANAGER_STORAGE', OverwriteStorage)

FIELD_FILEMANAGER_API_PERMISSIONS = get_cls('FIELD_FILEMANAGER_API_PERMISSIONS', (ModelHasPermission,))

FIELD_FILEMANAGER_STORAGE_CONFIG = getattr(settings, 'FIELD_FILEMANAGER_STORAGE_CONFIG', [])

FIELD_FILEMANAGER_STORAGE_DEFAULT_STORAGE = 'django.core.files.storage.FileSystemStorage'

FIELD_FILEMANAGER_STORAGE_PERMISSIONS = get_cls(
    'FIELD_FILEMANAGER_STORAGE_PERMISSIONS', (StorageHasPermission,))
