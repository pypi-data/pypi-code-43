import logging

from kaf_pas.kd.models.documents import Documents, DocumentManager, DocumentQuerySet

logger = logging.getLogger(__name__)


class CdwQuerySet(DocumentQuerySet):
    ...


class CdwManager(DocumentManager):
    def get_queryset(self):
        return CdwQuerySet(self.model, using=self._db).filter(attr_type__code='CDW')


class Cdws(Documents):
    objects = CdwManager()

    class Meta:
        verbose_name = 'Чертежи'
        proxy = True
