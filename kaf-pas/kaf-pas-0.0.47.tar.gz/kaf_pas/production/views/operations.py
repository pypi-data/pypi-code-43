from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.production.models.operations import Operations, OperationsManager
from kaf_pas.production.models.operations_view import Operations_view, Operations_viewManager


@JsonResponseWithException()
def Operations_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Operations_view.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Operations_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_Add(request):
    return JsonResponse(DSResponseAdd(data=Operations.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_Update(request):
    return JsonResponse(DSResponseUpdate(data=Operations.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Operations.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Operations.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_Info(request):
    return JsonResponse(DSResponse(request=request, data=Operations.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
