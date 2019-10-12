import logging

from django.db.models import DateTimeField

from crypto.models.crypto_file import Crypto_file, CryptoManager, CryptoQuerySet
from isc_common import delAttr
from isc_common.fields.code_field import CodeField
from isc_common.fields.description_field import DescriptionField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from kaf_pas.ckk.models.status import Status
from kaf_pas.sales.models.customer import Customer
from kaf_pas.sales.models.status_dogovor import StatusDogovor

logger = logging.getLogger(__name__)


class DogovorsQuerySet(CryptoQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class DogovorsManager(CryptoManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'date': record.date,
            'date_sign': record.date_sign,
            'description': record.description,

            'status_id': record.status.id if record.status else None,
            'status__code': record.status.code if record.status else None,
            'status__name': record.status.name if record.status else None,

            'customer_id': record.customer.id if record.customer else None,
            'customer__inn': record.customer.inn if record.customer else None,
            'customer__kpp': record.customer.kpp if record.customer else None,
            'customer__name': record.customer.name if record.customer else None,
            'customer__full_name': record.customer.full_name if record.customer else None,
            'customer__description': record.customer.description if record.customer else None,

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

    def updateFromRequest(self, request, printRequest=False):
        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()
        delAttr(_data, 'form')
        delAttr(_data, 'isFolder')
        super().filter(id=request.get_id()).update(**_data)
        return data

    def get_queryset(self):
        return DogovorsQuerySet(self.model, using=self._db)


class Dogovors(Crypto_file):
    code = CodeField()
    description = DescriptionField()
    parent = ForeignKeyProtect('self', null=True, blank=True, related_name='parent_d')

    date = DateTimeField(verbose_name='Дата', db_index=True, null=True, blank=True)
    date_sign = DateTimeField(verbose_name='Дата подписания', db_index=True, null=True, blank=True)

    status = ForeignKeyProtect(StatusDogovor, default=None)
    customer = ForeignKeyProtect(Customer, null=True, blank=True)

    objects = DogovorsManager()

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name = 'Документы'
