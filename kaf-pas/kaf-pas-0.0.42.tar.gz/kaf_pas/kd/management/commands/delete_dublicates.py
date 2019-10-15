import logging

from django.core.management import BaseCommand
from django.db import transaction, connection
from django.db.models import ProtectedError
from tqdm import tqdm

from kaf_pas.kd.models.documents import Documents
from kaf_pas.kd.models.documents_thumb import Documents_thumb
from kaf_pas.kd.models.documents_thumb10 import Documents_thumb10
from kaf_pas.kd.models.uploades_documents import Uploades_documents

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Удаление дубликатов чертежей"

    def handle(self, *args, **options):

        logger.info(self.help)

        sql_txt = '''select
                file_document,
                file_change_time,
                file_modification_time,
                path_id,
                deleted_at,
                count(*)
            from
                kd_documents
            group by
                file_document,
                file_change_time,
                path_id,
                deleted_at,
                file_modification_time
            having
                count(*) > 1'''

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(f'''select count(*)
                                  from ({sql_txt}) as a''')
                row = cursor.fetchone()
                self.pbar = tqdm(total=row[0])

                cursor.execute(sql_txt)
                row = cursor.fetchall()
                for p in row:
                    file_document = p[0]
                    logger.debug(f'\nDeleting: {file_document}')

                    for document in Documents.objects.filter(file_document=file_document):
                        Documents_thumb10.objects.filter(document=document).delete()
                        Documents_thumb.objects.filter(document=document).delete()
                        Uploades_documents.objects.filter(document=document).delete()
                        try:
                            res, _ = document.delete()
                            logger.debug(f'\n\nDFELETED {file_document}')
                        except ProtectedError:
                            logger.debug(f'\n\nNOT DFELETED {file_document}')

                    if self.pbar:
                        self.pbar.update(1)

                if self.pbar:
                    self.pbar.close()

        logger.info("Удаление выполнено")
