from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.sales.models.precent_items import Precent_items, Precent_itemsManager


@JsonResponseWithException()
def Precent_items_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Precent_items.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Precent_itemsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_items_Add(request):
    return JsonResponse(DSResponseAdd(data=Precent_items.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_items_Update(request):
    return JsonResponse(DSResponseUpdate(data=Precent_items.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_items_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Precent_items.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_items_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Precent_items.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_items_Info(request):
    return JsonResponse(DSResponse(request=request, data=Precent_items.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
