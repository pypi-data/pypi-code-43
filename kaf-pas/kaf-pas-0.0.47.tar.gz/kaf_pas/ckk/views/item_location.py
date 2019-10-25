from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.ckk.models.item_location import Item_location, Item_locationManager


@JsonResponseWithException()
def Item_location_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Item_location.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Item_locationManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_location_Add(request):
    return JsonResponse(DSResponseAdd(data=Item_location.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_location_Update(request):
    return JsonResponse(DSResponseUpdate(data=Item_location.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_location_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Item_location.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_location_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Item_location.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_location_Info(request):
    return JsonResponse(DSResponse(request=request, data=Item_location.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
