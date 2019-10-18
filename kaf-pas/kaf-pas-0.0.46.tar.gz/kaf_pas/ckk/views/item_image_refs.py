from isc_common.http.DSRequest import DSRequest
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.ckk.models.item_image_refs import Item_image_refs, Item_image_refsManager


@JsonResponseWithException()
def Item_image_refs_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Item_image_refs.objects.
                filter(thumb__isnull=False).
                get_range_rows1(
                request=request,
                function=Item_image_refsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_image_refs_Add(request):
    return JsonResponse(DSResponseAdd(data=Item_image_refs.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_image_refs_Update(request):
    return JsonResponse(DSResponseUpdate(data=Item_image_refs.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_image_refs_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Item_image_refs.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_image_refs_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Item_image_refs.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_image_refs_Info(request):
    return JsonResponse(DSResponse(request=request, data=Item_image_refs.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_image_refs_Copy(request):
    _request = DSRequest(request=request)

    source = _request.json.get('source')
    srecords = source.get('records')

    destination = _request.json.get('destination')
    drecords = destination.get('records')

    res = False
    if isinstance(srecords, list):
        for srecord in srecords:
            for drecord in drecords:
                if drecord.get('child_id'):
                    item_refs, _ = Item_image_refs.objects.get_or_create(item_id=drecord.get('child_id'), thumb_id=srecord.get('id'))
                else:
                    item_refs, _ = Item_image_refs.objects.get_or_create(item_id=drecord.get('id'), thumb_id=srecord.get('id'))
                res = True

    if not res:
        raise Exception('Вставка не выполнена!')

    return JsonResponse(DSResponse(request=request, status=RPCResponseConstant.statusSuccess).response)
