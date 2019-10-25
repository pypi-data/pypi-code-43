from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.sales.models.status_demand import Status_demand, Status_demandManager


@JsonResponseWithException()
def Status_demand_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Status_demand.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Status_demandManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Status_demand_Add(request):
    return JsonResponse(DSResponseAdd(data=Status_demand.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Status_demand_Update(request):
    return JsonResponse(DSResponseUpdate(data=Status_demand.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Status_demand_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Status_demand.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Status_demand_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Status_demand.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Status_demand_Info(request):
    return JsonResponse(DSResponse(request=request, data=Status_demand.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Status_demand_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Status_demand.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)            
