from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.sales.models.launches import Launches, LaunchesManager


@JsonResponseWithException()
def Launches_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Launches.objects.
                select_related('demand', 'status').
                get_range_rows1(
                request=request,
                function=LaunchesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launches_Add(request):
    return JsonResponse(DSResponseAdd(data=Launches.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launches_Update(request):
    return JsonResponse(DSResponseUpdate(data=Launches.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launches_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Launches.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launches_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Launches.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launches_Info(request):
    return JsonResponse(DSResponse(request=request, data=Launches.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launches_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Launches.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
