import logging
import os

from django.conf import settings
from django.db.models import BinaryField, BigIntegerField, CharField, TextField
from django.forms import model_to_dict
from isc_common import delAttr
from isc_common.fields.files import FileFieldEx
from isc_common.fields.name_field import NameField
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.audit import AuditModel

logger = logging.getLogger(__name__)

class CryptoQuerySet(CommonManagetWithLookUpFieldsQuerySet):

    def delete(self):
        for item in self:
            old_file_store = item.file_store
            file_path = item.attfile.name

            if old_file_store:
                file_path = file_path.replace(old_file_store, settings.FILES_STORE)

            if isinstance(settings.REPLACE_FILE_PATH, dict):
                for key, value in settings.REPLACE_FILE_PATH.items():
                    file_path = file_path.replace(key, value)

            if file_path:
                if os.altsep:
                    file_path = file_path.replace(os.altsep, os.sep)

                if os.path.exists(file_path):
                    res = os.remove(file_path)
                    logger.debug(f'Removed file: {file_path}')
                else:
                    logger.warning(f'Removed file: {file_path} not finded.')
        return super().delete()


class CryptoManager(CommonManagetWithLookUpFieldsManager):
    def createFromRequest(self, request, printRequest=False, function=None):
        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()
        for key in data:
            if key.find('__') != -1:
                delAttr(_data, key)
        delAttr(_data, 'form')
        if data.get('id') or not data.get('real_name'):
            delAttr(_data, 'id')
            res = super().update_or_create(id=data.get('id'), defaults=_data)
            res = model_to_dict(res[0])
            delAttr(res, 'attfile')
            delAttr(res, 'form')
            data.update(res)
        return data

    def updateFromRequest(self, request, printRequest=False):
        request = DSRequest(request=request)
        data = request.get_data()
        delAttr(data, 'form')
        super().filter(id=request.get_id()).update(**data)
        return data

    def get_queryset(self):
        return CryptoQuerySet(self.model, using=self._db)


class Crypto_file(AuditModel):
    format = NameField(verbose_name='Формат файла')
    mime_type = NameField(verbose_name='MIME тип файла файла', null=True, blank=True, default=None)
    size = BigIntegerField(verbose_name='Размер фала', default=0)
    real_name = TextField(verbose_name='Первоначальное имя файла', null=True, blank=True, default=None)
    key = BinaryField(max_length=200, null=True, blank=True)
    attfile = FileFieldEx(verbose_name='Файл', max_length=255, null=True, blank=True, default=None)
    file_store = CharField(verbose_name='Каталог хранения файла', max_length=255, null=True, blank=True)

    object = CryptoManager()

    def __str__(self):
        return f"{self.real_name}"

    class Meta:
        abstract = True
