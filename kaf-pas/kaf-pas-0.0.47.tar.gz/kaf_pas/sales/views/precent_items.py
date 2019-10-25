from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.sales.models.precent_items import Precent_items
from kaf_pas.sales.models.precent_items_view import Precent_items_view, Precent_items_viewManager


@JsonResponseWithException()
def Precent_items_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Precent_items_view.objects.
                select_related('item', 'precent_item_type', 'precent_dogovor').
                get_range_rows1(
                request=request,
                function=Precent_items_viewManager.getRecord
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
