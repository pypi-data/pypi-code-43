from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.ckk.models.ed_izm import Ed_izm, Ed_izmManager


@JsonResponseWithException()
def Ed_izm_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Ed_izm.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Ed_izmManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Ed_izm_Add(request):
    return JsonResponse(DSResponseAdd(data=Ed_izm.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Ed_izm_Update(request):
    return JsonResponse(DSResponseUpdate(data=Ed_izm.objects.updateFromRequest(request, removed=['isFolder']), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Ed_izm_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Ed_izm.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Ed_izm_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Ed_izm.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Ed_izm_Info(request):
    return JsonResponse(DSResponse(request=request, data=Ed_izm.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
