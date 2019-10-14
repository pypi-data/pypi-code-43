import os
import tempfile
from django.core.files.storage import FileSystemStorage
import django.core.files.storage


# dummy django.conf.settings
class Settings():
    MEDIA_ROOT = os.path.dirname(os.path.abspath(__file__))
    MEDIA_URL = 'http://local/'
    FILE_UPLOAD_PERMISSIONS = 0o777
    FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o777
    USE_TZ = False


# switch settings
django.core.files.storage.settings = Settings()


def get_test_storage():
    temp_dir = tempfile.mkdtemp()
    storage = FileSystemStorage(location=temp_dir, base_url='/')
    return temp_dir, storage


def get_storage(folder):
    storage = FileSystemStorage(location=folder, base_url='/')
    return storage
