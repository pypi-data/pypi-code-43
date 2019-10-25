import logging

from kaf_pas.kd.models.documents import Documents, DocumentManager, DocumentQuerySet

logger = logging.getLogger(__name__)


class PdfQuerySet(DocumentQuerySet):
    ...


class PdfManager(DocumentManager):
    def get_queryset(self):
        return PdfQuerySet(self.model, using=self._db).filter(attr_type__code='KD_PDF')


class Pdfs(Documents):
    objects = PdfManager()

    class Meta:
        verbose_name = 'Бумажные Чертежи'
        proxy = True
