import logging

from kaf_pas.kd.models.documents import Documents, DocumentManager, DocumentQuerySet

logger = logging.getLogger(__name__)


class SpwQuerySet(DocumentQuerySet):
    pass


class SpwManager(DocumentManager):
    def get_queryset(self):
        return SpwQuerySet(self.model, using=self._db).filter(attr_type__code='SPW')


class Spws(Documents):
    objects = SpwManager()

    class Meta:
        verbose_name = 'Спецификации'
        proxy = True
