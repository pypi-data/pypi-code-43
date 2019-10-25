from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.planing.models.prod_tasks import Prod_tasks, Prod_tasksManager


@JsonResponseWithException()
def Prod_tasks_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Prod_tasks.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Prod_tasksManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Prod_tasks_Add(request):
    return JsonResponse(DSResponseAdd(data=Prod_tasks.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Prod_tasks_Update(request):
    return JsonResponse(DSResponseUpdate(data=Prod_tasks.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Prod_tasks_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Prod_tasks.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Prod_tasks_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Prod_tasks.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Prod_tasks_Info(request):
    return JsonResponse(DSResponse(request=request, data=Prod_tasks.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Prod_tasks_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Prod_tasks.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)            
