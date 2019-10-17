from django.db import transaction, IntegrityError

from isc_common.http.DSRequest import DSRequest
from isc_common.http.RPCResponse import RPCResponseConstant
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.item_image_refs import Item_image_refs
from kaf_pas.ckk.models.item_line import Item_line
from kaf_pas.ckk.models.item_location import Item_location
from kaf_pas.ckk.models.item_refs import Item_refs
from kaf_pas.production.models.operations_item import Operations_item
from kaf_pas.sales.models.precent_items import Precent_items


class CombineItems(DSRequest):
    def __init__(self, request):
        DSRequest.__init__(self, request)
        data = self.get_data()

        recordTarget = data.get('recordTarget')
        if not isinstance(recordTarget, dict):
            raise Exception(f'recordTarget must be a dict')

        recordsSource = data.get('recordsSource')
        if not isinstance(recordsSource, list):
            raise Exception(f'recordsSource must be a list')

        # with transaction.atomic():
        for recordSource in recordsSource:
            if recordSource.get('id') != recordTarget.get('id'):
                for item_refs in Item_refs.objects.filter(child_id=recordSource.get('id')):
                    item_refs.child_id = recordTarget.get('id')
                    try:
                        item_refs.save()
                    except IntegrityError:
                        item_refs.delete()

                for item_refs in Item_refs.objects.filter(parent_id=recordSource.get('id')):
                    item_refs.parent_id = recordTarget.get('id')
                    try:
                        item_refs.save()
                    except IntegrityError:
                        item_refs.delete()

                for item_image_refs in Item_image_refs.objects.filter(item_id=recordSource.get('id')):
                    item_image_refs.item_id = recordTarget.get('id')
                    try:
                        item_image_refs.save()
                    except IntegrityError:
                        item_image_refs.delete()

                for item_line in Item_line.objects.filter(child_id=recordSource.get('id')):
                    item_line.child_id = recordTarget.get('id')
                    try:
                        item_line.save()
                    except IntegrityError:
                        item_line.delete()

                for item_line in Item_line.objects.filter(parent_id=recordSource.get('id')):
                    item_line.parent_id = recordTarget.get('id')
                    try:
                        item_line.save()
                    except IntegrityError:
                        item_line.delete()

                for item_location in Item_location.objects.filter(item_id=recordSource.get('id')):
                    item_location.item_id = recordTarget.get('id')
                    try:
                        item_location.save()
                    except IntegrityError:
                        item_location.delete()

                for operations_item in Operations_item.objects.filter(item_id=recordSource.get('id')):
                    operations_item.item_id = recordTarget.get('id')
                    try:
                        operations_item.save()
                    except IntegrityError:
                        operations_item.delete()

                for precent_items in Precent_items.objects.filter(item_id=recordSource.get('id')):
                    precent_items.item_id = recordTarget.get('id')
                    try:
                        precent_items.save()
                    except IntegrityError:
                        precent_items.delete()

                Item.objects.filter(id=recordSource.get('id')).delete()

        self.response = dict(status=RPCResponseConstant.statusSuccess)
