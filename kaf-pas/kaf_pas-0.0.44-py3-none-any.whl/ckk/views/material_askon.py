from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.ckk.models.material_askon import Material_askon
from kaf_pas.ckk.models.material_askon_mview import Material_askon_mview, Material_askon_mviewManager


@JsonResponseWithException()
def Material_askon_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Material_askon_mview.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Material_askon_mviewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_askon_Add(request):
    return JsonResponse(DSResponseAdd(data=Material_askon.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_askon_Update(request):
    return JsonResponse(DSResponseUpdate(data=Material_askon.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_askon_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Material_askon.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_askon_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Material_askon.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_askon_Info(request):
    return JsonResponse(DSResponse(request=request, data=Material_askon.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_askon_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Material_askon.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
