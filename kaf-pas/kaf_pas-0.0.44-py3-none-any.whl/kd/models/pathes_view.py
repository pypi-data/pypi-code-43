import logging
import os

from django.db import transaction
from django.db.models import BigIntegerField, TextField, BigAutoField, DateTimeField, BooleanField, Model, CharField
from django.forms import model_to_dict
from django.utils import timezone

from isc_common import delAttr
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from kaf_pas.kd.models.pathes import Pathes, PathesManager

logger = logging.getLogger(__name__)


class Pathes_viewManager(PathesManager):

    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            "path": record.path,
            "virt_path": record.virt_path,
            "parent_id": record.parent_id,
            "lastmodified": record.lastmodified,
            "editing": record.editing,
            "deliting": record.deliting,
            "isFolder": record.isFolder,
            "drive": record.drive,
        }
        return res

    def createFromRequest(self, request):
        request = DSRequest(request=request)

        data = request.get_data()
        delAttr(data, 'relevant')
        delAttr(data, 'ignored_on_load')
        delAttr(data, 'path_id')
        delAttr(data, 'isFolder')

        res = Pathes.objects.create(**data)
        res = model_to_dict(res)
        data.update(res)
        return data

    def updateFromRequest(self, request):
        request = DSRequest(request=request)

        with transaction.atomic():
            data = request.get_data()

            _data = data.copy()
            delAttr(_data, 'id')
            delAttr(_data, 'children')
            delAttr(_data, 'relevant')
            delAttr(_data, 'ignored_on_load')
            delAttr(_data, 'path_id')
            delAttr(_data, 'isFolder')
            Pathes.objects.filter(id=data.get('id')).update(**_data)
        return data


class Pathes_view(Model):
    id = BigAutoField(primary_key=True, verbose_name="Идентификатор")
    deleted_at = DateTimeField(verbose_name="Дата мягкого удаления", null=True, blank=True, db_index=True)
    editing = BooleanField(verbose_name="Возможность редактирования", default=True)
    deliting = BooleanField(verbose_name="Возможность удаления", default=True)
    lastmodified = DateTimeField(verbose_name='Последнее обновление', editable=False, db_index=True, default=timezone.now)

    isFolder = BooleanField()

    drive = CharField(max_length=10, null=True, blank=True)
    path = TextField(verbose_name="Путь")
    virt_path = TextField(verbose_name="Мнимый путь", null=True, blank=True)
    parent = ForeignKeyProtect("self", null=True, blank=True)

    @property
    def absolute_path(self):
        def get_parent(item_tuple):
            if item_tuple[0].parent:
                res = Pathes.objects.get(id=item_tuple[0].parent.id)
                res = (res, f"{res.path}/{item_tuple[1]}")
                return get_parent(res)
            else:
                return item_tuple

        if self.parent:
            res = get_parent((self, self.path))
            return f'{os.altsep}{res[1]}'
        else:
            return f'{os.altsep}{self.path}'

    def __str__(self):
        return f"{self.absolute_path}"

    objects = Pathes_viewManager()

    class Meta:
        db_table = 'kd_pathes_view'
        managed = False
        verbose_name = 'Пути нахождения документов'
