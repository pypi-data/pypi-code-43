from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.ckk.models.materials import Materials, MaterialsManager


@JsonResponseWithException()
def Materials_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Materials.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=MaterialsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Materials_Add(request):
    return JsonResponse(DSResponseAdd(data=Materials.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Materials_Update(request):
    return JsonResponse(DSResponseUpdate(data=Materials.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Materials_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Materials.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Materials_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Materials.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Materials_Info(request):
    return JsonResponse(DSResponse(request=request, data=Materials.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
