from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.kd.models.documents_history import Documents_history, Documents_historyManager


@JsonResponseWithException()
def Documents_history_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Documents_history.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Documents_historyManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_history_Add(request):
    return JsonResponse(DSResponseAdd(data=Documents_history.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_history_Update(request):
    return JsonResponse(DSResponseUpdate(data=Documents_history.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_history_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Documents_history.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_history_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Documents_history.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_history_Info(request):
    return JsonResponse(DSResponse(request=request, data=Documents_history.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_history_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Documents_history.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)            
