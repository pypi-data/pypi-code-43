import logging

from bitfield import BitField
from django.db.models import TextField, PositiveIntegerField, DateTimeField, BigAutoField, BigIntegerField, BooleanField, Model
from django.utils import timezone

from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from kaf_pas.ckk.models.attr_type import Attr_type
from kaf_pas.kd.models.document_attributes import Document_attributes
from kaf_pas.kd.models.documents import DocumentManager, Documents
from kaf_pas.kd.models.pathes import Pathes

logger = logging.getLogger(__name__)

class Documents_mviewManager(DocumentManager):
    def deleteFromRequest(self, request):
        _request = DSRequest(request=request)
        if _request.json:
            ids = _request.get_ids()
            old_ids = _request.get_old_ids()
        else:
            ids = dict(request.GET).get('ids')
            old_ids = []

        Documents.objects.filter(id__in=ids).delete()
        Documents.objects.filter(id__in=old_ids).delete()
        return []


class Documents_mview(Model):
    id = BigAutoField(primary_key=True, verbose_name="Идентификатор")
    deleted_at = DateTimeField(verbose_name="Дата мягкого удаления", null=True, blank=True, db_index=True)
    editing = BooleanField(verbose_name="Возможность редактирования", default=True)
    deliting = BooleanField(verbose_name="Возможность удаления", default=True)
    lastmodified = DateTimeField(verbose_name='Последнее обновление', editable=False, db_index=True, default=timezone.now)

    path = ForeignKeyProtect(Pathes, verbose_name='Путь к документу')
    relevant = CodeField(verbose_name='Актуальность')
    attr_type = ForeignKeyProtect(Attr_type, verbose_name='Тип документа')
    file_document = TextField(verbose_name='Полный путь к файлу')
    file_size = PositiveIntegerField(verbose_name='Размер файла')
    file_modification_time = DateTimeField(verbose_name='Дата время поcледнего модификации документа', null=True, blank=True)
    file_access_time = DateTimeField(verbose_name='Дата время поcледнего доступа к документу', null=True, blank=True)
    file_change_time = DateTimeField(verbose_name='Дата время изменнения документа', null=True, blank=True)
    props = BitField(flags=(('relevant', 'Актуальность'), ('beenItemed', 'Был внесен в состав изделий')), default=1)
    load_error = TextField(null=True, blank=True)

    STMP_1 = ForeignKeyProtect(Document_attributes, verbose_name='Наименование изделия', related_name='STMP_1_doc_mview', null=True, blank=True)
    STMP_2 = ForeignKeyProtect(Document_attributes, verbose_name='Обозначение изделия', related_name='STMP_2_doc_mview', null=True, blank=True)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'path_id': record.path.id,
            'attr_type_id': record.attr_type.id,
            'attr_type__code': record.attr_type.code,
            'attr_type__name': record.attr_type.name,
            "STMP_1_id": record.STMP_1.id if record.STMP_1 else None,
            "STMP_1__value_str": record.STMP_1.value_str if record.STMP_1 else None,
            "STMP_2_id": record.STMP_2.id if record.STMP_2 else None,
            "STMP_2__value_str": record.STMP_2.value_str if record.STMP_2 else None,
            'file_document': record.file_document,
            'file_size': record.file_size,
            'file_modification_time': record.file_modification_time,
            'file_access_time': record.file_access_time,
            'file_change_time': record.file_change_time,
            'relevant': record.relevant,
            'load_error': f'<pre>{record.load_error}</pre>' if record.load_error else None,
            'lastmodified': record.lastmodified,
            'editing': record.editing,
            'deliting': record.deliting,
            'props': record.props._value,
            'deleted_at': record.deleted_at,
        }
        return res

    def __str__(self):
        return f'ID: {self.id}, STMP_1: {self.STMP_1}, STMP_2: {self.STMP_2} file: {self.file_document}'

    objects = Documents_mviewManager()

    class Meta:
        managed = False
        db_table = 'kd_documents_mview'
        verbose_name = 'Documents MView'
