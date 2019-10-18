import logging

from django.db.models import DateTimeField, BigIntegerField, TextField, BooleanField

from isc_common.fields.code_field import CodeField
from isc_common.fields.description_field import DescriptionField
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from kaf_pas.sales.models.customer import Customer
from kaf_pas.sales.models.status_dogovor import StatusDogovor

logger = logging.getLogger(__name__)


class Dogovors_viewQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Dogovors_viewManager(AuditManager):

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
            'isFolder': record.isFolder,
            'parent_id': record.parent.id if record.parent else None,
        }
        return res

    def get_queryset(self):
        return Dogovors_viewQuerySet(self.model, using=self._db)


class Dogovors_view(AuditModel):
    code = CodeField()
    isFolder = BooleanField()
    description = DescriptionField()
    parent = ForeignKeyProtect('self', null=True, blank=True, related_name='parent_d_view')

    size = BigIntegerField(verbose_name='Размер фала', default=0)
    real_name = TextField(verbose_name='Первоначальное имя файла', null=True, blank=True, default=None)
    mime_type = NameField(verbose_name='MIME тип файла файла', null=True, blank=True, default=None)
    format = NameField(verbose_name='Формат файла')

    date = DateTimeField(verbose_name='Дата', db_index=True)
    date_sign = DateTimeField(verbose_name='Дата подписания', db_index=True, null=True, blank=True)

    status = ForeignKeyProtect(StatusDogovor, default=None)
    customer = ForeignKeyProtect(Customer, null=True, blank=True)

    objects = Dogovors_viewManager()

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name = 'Документы'
        db_table = 'sales_dogovors_view'
        managed = False
