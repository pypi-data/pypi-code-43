import logging
import os

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import TextField, CharField
from isc_common import delete_drive_leter, get_drive_leter
from isc_common.models.audit import AuditQuerySet, AuditManager
from isc_common.models.base_ref import Hierarcy

logger = logging.getLogger(__name__)


class PathesQuerySet(AuditQuerySet):
    def delete(self):
        from kaf_pas.kd.models.documents import Documents

        for item in self:
            Documents.objects.filter(path=item).delete()

        return super().delete()


class PathesManager(AuditManager):
    def get_queryset(self):
        return PathesQuerySet(self.model, using=self._db)

    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            "path": record.path,
            "virt_path": record.virt_path,
            "parent_id": record.parent_id,
            "lastmodified": record.lastmodified,
            "editing": record.editing,
            "drive": record.drive,
            "deliting": record.deliting,
            # "isFolder": record.isFolder,
        }
        return res

    @property
    def sep(self):
        return os.altsep if os.altsep else os.sep

    def create_ex(self, **kwargs):
        path = kwargs.get('path')
        parent = kwargs.get('parent')
        with_out_last = kwargs.get('with_out_last')

        if not path:
            raise Exception(f'path {path} is not exists.')

        if path:
            drive = get_drive_leter(path)
            path = delete_drive_leter(path)

            # if path != '' and path.find(self.sep) != -1:
            if path != '':
                if with_out_last:
                    path = path.split(self.sep)[: - 1]
                else:
                    path = path.split(self.sep)

                for path_item in path:
                    if path_item:
                        alive_only = self.alive_only
                        try:
                            self.alive_only = False
                            if drive and path == '':
                                parent = super().get(drive=drive, path=path_item, parent=parent)
                            else:
                                parent = super().get(path=path_item, parent=parent)
                            self.alive_only = alive_only
                        except ObjectDoesNotExist:
                            self.alive_only = alive_only
                            if drive and path == '':
                                parent = super().create(drive=drive, path=path_item, parent=parent)
                            else:
                                parent = super().create(path=path_item, parent=parent)
            else:
                parent, _ = super().get_or_create(drive=drive, parent=parent)

        return parent

    # Только для перенаправленных на виндовый сервак вызовов !!!!
    def deleteFromRequest(self, request, removed=None, ):
        ids = request.GET.getlist('ids')
        res = 0
        for i in range(0, len(ids), 2):
            if ids[i + 1] == 'hide':
                res += super().filter(id=ids[i]).soft_delete()
            else:
                res += super().filter(id=ids[i]).delete()[0]
        return res

    def get_drive(self, id):
        try:
            path = self.get(id=id)
            if path.drive:
                return path.drive
            elif path.parent:
                return self.get_drive(path.parent.id)
            else:
                return path.drive
        except Pathes.DoesNotExist:
            return None

    def get_drive(self, id):
        try:
            path = self.get(id=id)
            if path.drive:
                return path.drive
            elif path.parent:
                return self.get_drive(path.parent.id)
            else:
                return path.drive
        except Pathes.DoesNotExist:
            return None


class Pathes(Hierarcy):
    drive = CharField(verbose_name='Диск', max_length=10, null=True, blank=True)
    path = TextField(verbose_name="Путь")
    virt_path = TextField(verbose_name="Мнимый путь", null=True, blank=True)

    @property
    def sep(self):
        return os.altsep if os.altsep else os.sep

    def get_virt_path(self, id=None):
        try:
            path = Pathes.objects.get(id=id if id else self.id)
            if path.virt_path:
                return path.virt_path
            elif path.parent:
                return self.get_virt_path(path.parent.id)
            else:
                return path.virt_path
        except Pathes.DoesNotExist:
            return None

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
            return f'{self.sep}{res[1]}'
        else:
            return f'{self.sep}{self.path}'

    def get_drive(self, id=None):
        try:
            path = Pathes.objects.get(id=id if id else self.id)
            if path.drive:
                return path.drive
            elif path.parent:
                return self.get_drive(path.parent.id)
            else:
                return path.drive
        except Pathes.DoesNotExist:
            return None

    @property
    def drived_absolute_path(self):
        drive = self.get_drive(self.id)
        if drive:
            return f'{drive}{self.absolute_path}'
        else:
            return self.absolute_path

    def __str__(self):
        return f"{self.absolute_path}"

    objects = PathesManager()

    # def save(self, *args, **kwargs):
    #     if self.drived_absolute_path == None and self.STMP_2 == None:
    #         raise Exception(f'STMP_1 and STMP_2 not been Null together. ({self})')
    #     else:
    #         try:
    #             Item.objects.get(STMP_1=self.STMP_1, STMP_2=self.STMP_2, props=Item.props.relevant)
    #             logger.debug(f'Товарная позиция {self} существует в актуальном состоянии.')
    #         except self.DoesNotExist:
    #             pass
    #     super().save(*args, **kwargs)

    class Meta:
        db_table = 'pathes'
        verbose_name = 'Пути нахождения документов'
