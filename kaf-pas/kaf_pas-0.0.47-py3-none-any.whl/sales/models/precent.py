import logging

from django.db import transaction
from django.db.models import DateTimeField
from django.forms import model_to_dict

from crypto.models.crypto_file import Crypto_file, CryptoManager, CryptoQuerySet
from isc_common import delAttr, setAttr
from isc_common.fields.code_field import CodeField
from isc_common.fields.description_field import DescriptionField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from kaf_pas.sales.models.status_precent import StatusPrecent

logger = logging.getLogger(__name__)


class PrecentQuerySet(CryptoQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class PrecentManager(CryptoManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'date': record.date,
            'date_sign': record.date_sign,
            'description': record.description,

            'status_id': record.status.id,
            'status__code': record.status.code,
            'status__name': record.status.name,

            'format': record.format,
            'mime_type': record.mime_type,
            'size': record.size if not str(record.size).startswith('.') else str(record.size).replace('.', '0.'),
            'real_name': record.real_name,

            'lastmodified': record.lastmodified,
            'editing': record.editing,
            'deliting': record.deliting,
            'parent_id': record.parent.id if record.parent else None,
        }
        return res

    def createFromRequest(self, request, printRequest=False, function=None):
        from kaf_pas.sales.models.precent_dogovors import Precent_dogovors
        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()
        for key in data:
            if key.find('__') != -1:
                delAttr(_data, key)
        delAttr(_data, 'form')

        with transaction.atomic():
            document = data.get('document')
            if isinstance(document, list):
                delAttr(_data, 'document')
                for document_id in document:
                    if data.get('id') or not data.get('real_name'):
                        delAttr(_data, 'id')
                        res, _ = super().get_or_create(id=data.get('id'), defaults=_data)

                        Precent_dogovors.objects.get_or_create(dogovor_id=document_id, precent=res)
                        res = model_to_dict(res)
                        delAttr(res, 'attfile')
                        delAttr(res, 'form')
                        data.update(res)
            else:
                if data.get('id') or not data.get('real_name'):
                    delAttr(_data, 'id')
                    setAttr(_data, 'document_id', document)
                    res, _ = super().get_or_create(id=data.get('id'), defaults=_data)
                    Precent_dogovors.objects.get_or_create(dogovor_id=_data.get('document_id'), precent=res)
                    res = model_to_dict(res)
                    delAttr(res, 'attfile')
                    delAttr(res, 'form')
                    data.update(res)

        return data

    def updateFromRequest(self, request, printRequest=False):
        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()
        # data.update(dict(type))
        delAttr(_data, 'form')
        delAttr(_data, 'isFolder')
        super().filter(id=request.get_id()).update(**_data)
        return data

    def get_queryset(self):
        return PrecentQuerySet(self.model, using=self._db)


class Precent(Crypto_file):
    code = CodeField()
    description = DescriptionField()
    parent = ForeignKeyProtect('self', null=True, blank=True, related_name='parent_p')

    date = DateTimeField(verbose_name='Дата', db_index=True)
    date_sign = DateTimeField(verbose_name='Дата подписания', db_index=True, null=True, blank=True)

    status = ForeignKeyProtect(StatusPrecent)

    objects = PrecentManager()

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name = 'Распоряжение'
