from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.sales.models.precent_materials import Precent_materials, Precent_materialsManager


@JsonResponseWithException()
def Precent_materials_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Precent_materials.objects.
                select_related('edizm', 'material', 'material_askon', 'precent_item').
                get_range_rows1(
                request=request,
                function=Precent_materialsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_materials_Add(request):
    return JsonResponse(DSResponseAdd(data=Precent_materials.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_materials_Update(request):
    return JsonResponse(DSResponseUpdate(data=Precent_materials.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_materials_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Precent_materials.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_materials_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Precent_materials.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_materials_Info(request):
    return JsonResponse(DSResponse(request=request, data=Precent_materials.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
