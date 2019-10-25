from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.production.models.operation_material import Operation_material, Operation_materialManager


@JsonResponseWithException()
def Operation_material_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Operation_material.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Operation_materialManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_material_Add(request):
    return JsonResponse(DSResponseAdd(data=Operation_material.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_material_Update(request):
    return JsonResponse(DSResponseUpdate(data=Operation_material.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_material_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Operation_material.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_material_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Operation_material.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_material_Info(request):
    return JsonResponse(DSResponse(request=request, data=Operation_material.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
