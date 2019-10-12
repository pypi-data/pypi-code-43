from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.ckk.models.locations import Locations, LocationsManager


@JsonResponseWithException()
def Locations_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Locations.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=LocationsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Locations_Add(request):
    return JsonResponse(DSResponseAdd(data=Locations.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Locations_Update(request):
    return JsonResponse(DSResponseUpdate(data=Locations.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Locations_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Locations.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Locations_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Locations.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Locations_Info(request):
    return JsonResponse(DSResponse(request=request, data=Locations.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
