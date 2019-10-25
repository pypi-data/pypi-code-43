from django.db import transaction
from django.forms import model_to_dict

from isc_common import delAttr, setAttr, getAttr
from isc_common.http.DSRequest import DSRequest
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.ckk.models.combineItems import CombineItems
from kaf_pas.ckk.models.copyItems import CopyItems
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.item_line import Item_line
from kaf_pas.ckk.models.item_operations_view import Item_operations_view, Item_operations_viewManager
from kaf_pas.ckk.models.item_refs import Item_refs
from kaf_pas.ckk.models.item_view import Item_view, Item_viewManager


def Item_view_query():
    query = Item_view.objects.filter()
    return query


@JsonResponseWithException()
def Item_view_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Item_view_query().
                get_range_rows1(
                request=request,
                function=Item_viewManager.getRecord,
                distinct_field_names=('id',)
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_view_Fetch1(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Item_operations_view.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Item_operations_viewManager.getRecord,
                distinct_field_names=('id',)
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_view_Add(request):
    return JsonResponse(DSResponseAdd(data=Item.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_view_Update(request):
    return JsonResponse(DSResponseUpdate(data=Item.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_view_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Item.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_view_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Item.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_view_Info(request):
    return JsonResponse(DSResponse(request=request, data=Item_view_query().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_view_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Item_view.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException(printing=False)
def copyItems(request):
    return JsonResponse(CopyItems(request).response)


@JsonResponseWithException(printing=False)
def combineItems(request):
    return JsonResponse(CombineItems(request).response)


@JsonResponseWithException()
def Item_view_CopyBlockItems(request):
    _request = DSRequest(request=request)
    source = _request.json.get('source')
    destination = _request.json.get('destination')

    if isinstance(source, dict) and isinstance(destination, dict):
        srecords = source.get('records')
        drecord = destination.get('record')

        if isinstance(srecords, list) and isinstance(drecord, dict):
            with transaction.atomic():
                for srecord in srecords:
                    item_refs, created = Item_refs.objects.get_or_create(parent_id=drecord.get('id'), child_id=srecord.get('child_id'))
                    item_line = Item_line.objects.get(id=srecord.get('id'))
                    dict_item_line = model_to_dict(item_line)
                    delAttr(dict_item_line, 'id')
                    setAttr(dict_item_line, 'parent_id', drecord.get('id'))
                    delAttr(dict_item_line, 'parent')
                    setAttr(dict_item_line, 'child_id', getAttr(dict_item_line, 'child'))
                    delAttr(dict_item_line, 'child')

                    setAttr(dict_item_line, 'SPC_CLM_FORMAT_id', getAttr(dict_item_line, 'SPC_CLM_FORMAT'))
                    delAttr(dict_item_line, 'SPC_CLM_FORMAT')
                    setAttr(dict_item_line, 'SPC_CLM_ZONE_id', getAttr(dict_item_line, 'SPC_CLM_ZONE'))
                    delAttr(dict_item_line, 'SPC_CLM_ZONE')
                    setAttr(dict_item_line, 'SPC_CLM_POS_id', getAttr(dict_item_line, 'SPC_CLM_POS'))
                    delAttr(dict_item_line, 'SPC_CLM_POS')
                    setAttr(dict_item_line, 'SPC_CLM_MARK_id', getAttr(dict_item_line, 'SPC_CLM_MARK'))
                    delAttr(dict_item_line, 'SPC_CLM_MARK')
                    setAttr(dict_item_line, 'SPC_CLM_NAME_id', getAttr(dict_item_line, 'SPC_CLM_NAME'))
                    delAttr(dict_item_line, 'SPC_CLM_NAME')
                    setAttr(dict_item_line, 'SPC_CLM_COUNT_id', getAttr(dict_item_line, 'SPC_CLM_COUNT'))
                    delAttr(dict_item_line, 'SPC_CLM_COUNT')
                    setAttr(dict_item_line, 'SPC_CLM_NOTE_id', getAttr(dict_item_line, 'SPC_CLM_NOTE'))
                    delAttr(dict_item_line, 'SPC_CLM_NOTE')
                    setAttr(dict_item_line, 'SPC_CLM_MASSA_id', getAttr(dict_item_line, 'SPC_CLM_MASSA'))
                    delAttr(dict_item_line, 'SPC_CLM_MASSA')
                    setAttr(dict_item_line, 'SPC_CLM_MATERIAL_id', getAttr(dict_item_line, 'SPC_CLM_MATERIAL'))
                    delAttr(dict_item_line, 'SPC_CLM_MATERIAL')
                    setAttr(dict_item_line, 'SPC_CLM_USER_id', getAttr(dict_item_line, 'SPC_CLM_USER'))
                    delAttr(dict_item_line, 'SPC_CLM_USER')
                    setAttr(dict_item_line, 'SPC_CLM_KOD_id', getAttr(dict_item_line, 'SPC_CLM_KOD'))
                    delAttr(dict_item_line, 'SPC_CLM_KOD')
                    setAttr(dict_item_line, 'SPC_CLM_FACTORY_id', getAttr(dict_item_line, 'SPC_CLM_FACTORY'))
                    delAttr(dict_item_line, 'SPC_CLM_FACTORY')
                    parent_id = getAttr(dict_item_line, 'parent_id')
                    delAttr(dict_item_line, 'parent_id')
                    child_id = getAttr(dict_item_line, 'child_id')
                    delAttr(dict_item_line, 'child_id')
                    item_line, created = Item_line.objects.get_or_create(parent_id=parent_id, child_id=child_id, defaults=dict_item_line)

    return JsonResponse(DSResponse(request=request, status=RPCResponseConstant.statusSuccess).response)
