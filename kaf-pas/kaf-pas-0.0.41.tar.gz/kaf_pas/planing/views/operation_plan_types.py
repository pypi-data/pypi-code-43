from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.planing.models.operation_plan_types import Operation_plan_types, Operation_plan_typesManager


@JsonResponseWithException()
def Operation_plan_types_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Operation_plan_types.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Operation_plan_typesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_plan_types_Add(request):
    return JsonResponse(DSResponseAdd(data=Operation_plan_types.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_plan_types_Update(request):
    return JsonResponse(DSResponseUpdate(data=Operation_plan_types.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_plan_types_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Operation_plan_types.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_plan_types_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Operation_plan_types.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_plan_types_Info(request):
    return JsonResponse(DSResponse(request=request, data=Operation_plan_types.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_plan_types_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Operation_plan_types.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)            
