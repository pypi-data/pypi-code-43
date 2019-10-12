from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.production.models.operation_resources import Operation_resources, Operation_resourcesManager


@JsonResponseWithException()
def Operation_resources_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Operation_resources.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Operation_resourcesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_resources_Add(request):
    return JsonResponse(DSResponseAdd(data=Operation_resources.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_resources_Update(request):
    return JsonResponse(DSResponseUpdate(data=Operation_resources.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_resources_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Operation_resources.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_resources_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Operation_resources.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_resources_Info(request):
    return JsonResponse(DSResponse(request=request, data=Operation_resources.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
