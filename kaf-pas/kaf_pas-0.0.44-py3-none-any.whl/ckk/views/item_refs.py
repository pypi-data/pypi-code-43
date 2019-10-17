from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.ckk.models.item_refs import Item_refs


@JsonResponseWithException()
def Item_refs_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Item_refs.objects.
                filter().
                get_range_rows1(
                request=request,
                #function=XXX.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_refs_Add(request):
    return JsonResponse(DSResponseAdd(data=Item_refs.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_refs_Update(request):
    return JsonResponse(DSResponseUpdate(data=Item_refs.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_refs_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Item_refs.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_refs_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Item_refs.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_refs_Info(request):
    return JsonResponse(DSResponse(request=request, data=Item_refs.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
