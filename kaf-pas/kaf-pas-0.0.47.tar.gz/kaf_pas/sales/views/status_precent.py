from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.sales.models.status_precent import StatusPrecent, StatusPrecentManager


@JsonResponseWithException()
def StatusPrecent_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=StatusPrecent.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=StatusPrecentManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def StatusPrecent_Add(request):
    return JsonResponse(DSResponseAdd(data=StatusPrecent.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def StatusPrecent_Update(request):
    return JsonResponse(DSResponseUpdate(data=StatusPrecent.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def StatusPrecent_Remove(request):
    return JsonResponse(DSResponse(request=request, data=StatusPrecent.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def StatusPrecent_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=StatusPrecent.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def StatusPrecent_Info(request):
    return JsonResponse(DSResponse(request=request, data=StatusPrecent.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def StatusPrecent_Copy(request):
    return JsonResponse(DSResponse(request=request, data=StatusPrecent.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)            
