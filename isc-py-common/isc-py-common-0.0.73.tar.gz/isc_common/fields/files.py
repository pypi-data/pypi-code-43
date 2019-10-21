from django.conf import settings
from django.db.models import FileField
from django.db.models.fields.files import FieldFile
from isc_common.fields import Field


class FieldFileEx(FieldFile, Field):
    def open(self, mode='rb'):
        self._require_file()
        if getattr(self, '_file', None) is None:
            if isinstance(settings.REPLACE_FILE_PATH, dict):
                for key, value in settings.REPLACE_FILE_PATH.items():
                    self.name = self.name.replace(key, value)
            self.file = self.storage.open(self.name, mode)
        else:
            self.file.open(mode)
        return self


class FileFieldEx(FileField):
    attr_class = FieldFileEx
