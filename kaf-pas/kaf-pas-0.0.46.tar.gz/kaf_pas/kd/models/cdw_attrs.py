import logging

from isc_common import setAttr
from isc_common.http.DSRequest import DSRequest
from kaf_pas.kd.models.document_attrs_view import Document_attrs_view, Document_attrs_viewQuerySet, Document_attrs_viewManager

logger = logging.getLogger(__name__)


class Cdw_attrsQuerySet(Document_attrs_viewQuerySet):
    def filter(self, *args, **kwargs):
        setAttr(kwargs, 'attr_type__code__contains', 'STMP')
        return super().filter(*args, **kwargs)


class Cdw_attrsManager(Document_attrs_viewManager):

    def get_queryset(self):
        return Cdw_attrsQuerySet(self.model, using=self._db)

    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            "attr_type_id": record.attr_type.id,
            "attr_type__code": record.attr_type.code,
            "attr_type__name": record.attr_type.name,
            "attr_type__description": record.attr_type.description if record.attr_type else None,
            "section": record.section,
            "subsection": record.subsection,
            "value_str": record.value_str,
            "lastmodified": record.lastmodified,
            "editing": record.editing,
            "deliting": record.deliting,
        }
        return res


class Cdw_attrs(Document_attrs_view):
    objects = Cdw_attrsManager()

    class Meta:
        verbose_name = 'Чертеж'
        proxy = True
        managed = False
