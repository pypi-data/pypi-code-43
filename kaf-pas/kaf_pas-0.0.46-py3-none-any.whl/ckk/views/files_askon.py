from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.ckk.models.files_askon import Files_askon


@JsonResponseWithException()
def Files_askon_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Files_askon.objects.
                select_related().
                get_range_rows1(
                request=request,
                # function=Files_askonManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Files_askon_Add(request):
    return JsonResponse(DSResponseAdd(data=Files_askon.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Files_askon_Update(request):
    return JsonResponse(DSResponseUpdate(data=Files_askon.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Files_askon_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Files_askon.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Files_askon_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Files_askon.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Files_askon_Info(request):
    return JsonResponse(DSResponse(request=request, data=Files_askon.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Files_askon_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Files_askon.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)            
