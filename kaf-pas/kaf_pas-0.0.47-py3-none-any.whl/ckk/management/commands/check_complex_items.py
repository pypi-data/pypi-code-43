import logging

from django.core.management import BaseCommand
from django.db import transaction
from tqdm import tqdm

from isc_common import del_last_not_digit
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.item_complex_view import Item_Complex_view
from kaf_pas.ckk.models.item_line import Item_line
from kaf_pas.ckk.models.item_refs import Item_refs
from kaf_pas.ckk.models.item_view import Item_view

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Загрузка сборочных едениц"
    parent_list = []

    def isComplexItemTrue(self, item):
        res = Item_line.objects.filter(parent=item).count()
        return res > 0

    def isComplexItem(self, parent, child):
        try:
            item_line = Item_line.objects.get(parent=parent, child=child)
            return item_line.section == 'Сборочные единицы'
        except Item_line.DoesNotExist:
            return False

    cnt = 1

    def check_layer(self, parent=None, child_id=None, level=0):
        if not parent or (not parent.id in self.parent_list):
            if parent:
                self.parent_list.append(parent.id)
            logger.debug(f'\n\nLevel: {level}\n\n')

            if child_id:
                query = Item_view.objects.filter(
                    parent_id=parent.id if parent else None,
                    id=child_id,
                    props__in=[
                        Item.props.relevant | Item.props.from_spw,
                        Item.props.relevant | Item.props.from_spw | Item.props.for_line,
                        Item.props.relevant | Item.props.man_input
                    ]
                )
            else:
                query = Item_view.objects.filter(
                    parent_id=parent.id if parent else None,
                    props__in=[
                        Item.props.relevant | Item.props.from_spw,
                        Item.props.relevant | Item.props.from_spw | Item.props.for_line,
                        Item.props.relevant | Item.props.man_input
                    ]
                )

            for item_view in query:
                child = item_view.item
                # logger.debug(f'\n{child}')

                for item_line in Item_line.objects.filter(parent=child):
                    # logger.debug(item_line)
                    if self.isComplexItem(parent=item_line.parent, child=item_line.child):
                        if not self.isComplexItemTrue(item_line.child):
                            if item_line.child.STMP_2:
                                STMP_2 = del_last_not_digit(item_line.child.STMP_2.value_str)

                                complex_query = Item_Complex_view.objects.filter(STMP_2__value_str=STMP_2)
                                # logger.debug(f'complex_query len: {len(complex_query)}')
                                for complex_item in complex_query.distinct('STMP_2'):
                                    # logger.debug(f'\nFound complex Item: {complex_item}')

                                    item_line_new, created = Item_line.objects.get_or_create(parent=item_line.parent,
                                                                                             child=complex_item.item,
                                                                                             defaults=dict(
                                                                                                 SPC_CLM_FORMAT=item_line.SPC_CLM_FORMAT,
                                                                                                 SPC_CLM_ZONE=item_line.SPC_CLM_ZONE,
                                                                                                 SPC_CLM_POS=item_line.SPC_CLM_POS,
                                                                                                 SPC_CLM_COUNT=item_line.SPC_CLM_COUNT,
                                                                                                 SPC_CLM_NOTE=item_line.SPC_CLM_NOTE,
                                                                                                 SPC_CLM_MASSA=item_line.SPC_CLM_MASSA,
                                                                                                 SPC_CLM_MATERIAL=item_line.SPC_CLM_MATERIAL,
                                                                                                 SPC_CLM_USER=item_line.SPC_CLM_USER,
                                                                                                 SPC_CLM_KOD=item_line.SPC_CLM_KOD,
                                                                                                 SPC_CLM_FACTORY=item_line.SPC_CLM_FACTORY,
                                                                                                 SPC_CLM_NAME=complex_item.STMP_1,
                                                                                                 SPC_CLM_MARK=complex_item.STMP_2,
                                                                                                 section=item_line.section,
                                                                                                 subsection=item_line.subsection,
                                                                                             ))

                                    if created:
                                        logger.debug(f'\n#{self.cnt} Created item_line_new:{item_line_new}')
                                    else:
                                        logger.debug(f'\nn#{self.cnt} Founded item_line_new:{item_line_new}')

                                    self.cnt += 1

                                    item_refs, created = Item_refs.objects.get_or_create(parent=item_line.parent, child=complex_item.item)

                                    if created:
                                        logger.debug(f'\nCreated item_refs:{item_refs}')
                                    else:
                                        logger.debug(f'\nFounded item_refs:{item_refs}')

                                    res = Item_line.objects.filter(parent=item_line.parent, child=item_line.child).delete()
                                    # logger.debug(f'\nDeleted: {res[0]} from Item_line')
                                    res = Item_refs.objects.filter(parent=item_line.parent, child=item_line.child).delete()
                                    # logger.debug(f'\nDeleted: {res[0]} from Item_refs')
                                    break

                self.check_layer(parent=child, level=level + 1)
                logger.debug(f'\n\nLevel: {level}\n\n')

                if self.pbar:
                    self.pbar.update(1)

    def handle(self, *args, **options):

        logger.debug(self.help)

        self.pbar = tqdm(total=Item_view.objects.filter().count())

        # <editor-fold desc="Этап 3">
        with transaction.atomic():
            # self.check_layer(parent=Item.objects.get(id=3169551), child_id= 3169568)
            self.check_layer()
        logger.debug("Загрузка выполнена.")

        if self.pbar:
            self.pbar.close()

        # </editor-fold>

# with transaction.atomic():
