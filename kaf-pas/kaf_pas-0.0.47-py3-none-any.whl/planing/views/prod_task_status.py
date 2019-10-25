from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.planing.models.prod_task_status import Prod_task_statusManager, Prod_task_status


@JsonResponseWithException()
def Prod_task_status_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Prod_task_status.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Prod_task_statusManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Prod_task_status_Add(request):
    return JsonResponse(DSResponseAdd(data=Prod_task_status.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Prod_task_status_Update(request):
    return JsonResponse(DSResponseUpdate(data=Prod_task_status.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Prod_task_status_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Prod_task_status.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Prod_task_status_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Prod_task_status.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Prod_task_status_Info(request):
    return JsonResponse(DSResponse(request=request, data=Prod_task_status.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Prod_task_status_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Prod_task_status.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)            
