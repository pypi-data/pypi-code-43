from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.kd.models.uploades_log import Uploades_log, Uploades_logManager


@JsonResponseWithException()
def Uploades_log_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Uploades_log.objects.
                select_related('upload', ).
                get_range_rows1(
                request=request,
                function=Uploades_logManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Uploades_log_Add(request):
    return JsonResponse(DSResponseAdd(data=Uploades_log.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Uploades_log_Update(request):
    return JsonResponse(DSResponseUpdate(data=Uploades_log.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Uploades_log_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Uploades_log.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Uploades_log_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Uploades_log.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Uploades_log_Info(request):
    return JsonResponse(DSResponse(request=request, data=Uploades_log.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Uploades_log_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Uploades_log.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
