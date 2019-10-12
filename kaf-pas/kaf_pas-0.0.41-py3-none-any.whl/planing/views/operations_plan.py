from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.planing.models.operations_plan import OperationsPlanManager, OperationsPlan


@JsonResponseWithException()
def Operations_plan_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=OperationsPlan.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=OperationsPlanManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_plan_Add(request):
    return JsonResponse(DSResponseAdd(data=OperationsPlan.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_plan_Update(request):
    return JsonResponse(DSResponseUpdate(data=OperationsPlan.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_plan_Remove(request):
    return JsonResponse(DSResponse(request=request, data=OperationsPlan.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_plan_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=OperationsPlan.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_plan_Info(request):
    return JsonResponse(DSResponse(request=request, data=OperationsPlan.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_plan_Copy(request):
    return JsonResponse(DSResponse(request=request, data=OperationsPlan.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
