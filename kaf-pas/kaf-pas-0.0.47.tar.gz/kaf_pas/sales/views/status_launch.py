from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.sales.models.status_launch import Status_launch, Status_launchManager


@JsonResponseWithException()
def Status_launch_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Status_launch.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Status_launchManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Status_launch_Add(request):
    return JsonResponse(DSResponseAdd(data=Status_launch.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Status_launch_Update(request):
    return JsonResponse(DSResponseUpdate(data=Status_launch.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Status_launch_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Status_launch.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Status_launch_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Status_launch.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Status_launch_Info(request):
    return JsonResponse(DSResponse(request=request, data=Status_launch.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Status_launch_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Status_launch.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)            
