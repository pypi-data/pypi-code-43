from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.planing.models.operations_plan_status import OperationsPlanStatus, OperationsPlanStatusManager


@JsonResponseWithException()
def OperationsPlanStatus_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=OperationsPlanStatus.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=OperationsPlanStatusManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def OperationsPlanStatus_Add(request):
    return JsonResponse(DSResponseAdd(data=OperationsPlanStatus.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def OperationsPlanStatus_Update(request):
    return JsonResponse(DSResponseUpdate(data=OperationsPlanStatus.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def OperationsPlanStatus_Remove(request):
    return JsonResponse(DSResponse(request=request, data=OperationsPlanStatus.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def OperationsPlanStatus_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=OperationsPlanStatus.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def OperationsPlanStatus_Info(request):
    return JsonResponse(DSResponse(request=request, data=OperationsPlanStatus.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def OperationsPlanStatus_Copy(request):
    return JsonResponse(DSResponse(request=request, data=OperationsPlanStatus.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)            
