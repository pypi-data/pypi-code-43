from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.sales.models.demand_materials import Demand_materials, Demand_materialsManager


@JsonResponseWithException()
def Demand_materials_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Demand_materials.objects.
                select_related('demand', 'precent_material').
                get_range_rows1(
                request=request,
                function=Demand_materialsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Demand_materials_Add(request):
    return JsonResponse(DSResponseAdd(data=Demand_materials.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Demand_materials_Update(request):
    return JsonResponse(DSResponseUpdate(data=Demand_materials.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Demand_materials_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Demand_materials.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Demand_materials_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Demand_materials.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Demand_materials_Info(request):
    return JsonResponse(DSResponse(request=request, data=Demand_materials.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Demand_materials_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Demand_materials.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
