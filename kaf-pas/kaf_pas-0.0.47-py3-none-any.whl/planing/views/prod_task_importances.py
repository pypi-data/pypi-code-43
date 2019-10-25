from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.planing.models.prod_task_importances import Prod_task_importances, Prod_task_importancesManager


@JsonResponseWithException()
def Prod_task_importances_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Prod_task_importances.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Prod_task_importancesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Prod_task_importances_Add(request):
    return JsonResponse(DSResponseAdd(data=Prod_task_importances.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Prod_task_importances_Update(request):
    return JsonResponse(DSResponseUpdate(data=Prod_task_importances.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Prod_task_importances_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Prod_task_importances.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Prod_task_importances_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Prod_task_importances.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Prod_task_importances_Info(request):
    return JsonResponse(DSResponse(request=request, data=Prod_task_importances.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Prod_task_importances_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Prod_task_importances.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)            
