import logging

from django.core.management import BaseCommand
from django.db import transaction
from tqdm import tqdm

from kaf_pas.ckk.models.attr_type import Attr_type
from kaf_pas.kd.models.document_attr_cross import Document_attr_cross
from kaf_pas.kd.models.document_attributes import Document_attributes
from kaf_pas.kd.models.document_attributes_view import Document_attributes_view

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Перенос атрибутов КД"

    def handle(self, *args, **options):

        logger.info(self.help)

        self.pbar = tqdm(total=Document_attributes_view.objects.filter().count())

        section_attr_id, _ = Attr_type.objects.get_or_create(code='section', name='Секция')
        sub_section_attr_id, _ = Attr_type.objects.get_or_create(code='subsection', name='Подсекция')

        c = 0
        u = 0
        with transaction.atomic():
            document_id = None

            for attribute in Document_attributes_view.objects.filter():
                if document_id != attribute.document.id:
                    document_id =  attribute.document.id
                    position_in_document = 0

                attr, created = Document_attributes.objects.get_or_create(
                    attr_type=attribute.attr_type,
                    value_str=attribute.value_str,
                )

                if created:
                    c += 1
                    logger.debug(f'{attr} been created ({c} times)')
                else:
                    u += 1
                    logger.debug(f'{attr} been used ({u} times)')

                Document_attr_cross.objects.create(
                    document=attribute.document,
                    section=attribute.section,
                    subsection=attribute.subsection,
                    position_in_document=position_in_document,
                    attribute=attr
                )

                position_in_document += 1

                if self.pbar:
                    self.pbar.update(1)

        if self.pbar:
            self.pbar.close()

    logger.info("Перенос выполнен.")
    # </editor-fold>

# with transaction.atomic():
