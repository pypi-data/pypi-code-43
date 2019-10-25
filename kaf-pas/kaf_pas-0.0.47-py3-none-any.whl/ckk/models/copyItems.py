import logging

from django.db import transaction

from isc_common.http.DSRequest import DSRequest
from isc_common.http.RPCResponse import RPCResponseConstant
from kaf_pas.ckk.models.item_refs import Item_refs

logger = logging.getLogger(__name__)

class CopyItems(DSRequest):
    def __init__(self, request):
        DSRequest.__init__(self, request)
        data = self.get_data()

        source = data.get('source')
        desctination = data.get('destination')

        with transaction.atomic():
            Item_refs.objects.filter(id=desctination).select_for_update()
            if isinstance(source, list):
                for src in source:
                    Item_refs.objects.filter(id=src).select_for_update()
                    Item_refs.objects.create(parent_id=desctination, child_id=src)
                    Item_refs.objects.filter(parent__isnull=True, child_id=src).delete()

        self.response = dict(status=RPCResponseConstant.statusSuccess)
