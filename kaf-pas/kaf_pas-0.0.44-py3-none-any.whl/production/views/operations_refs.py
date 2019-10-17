from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.production.models.operations_refs import Operations_refs, Operations_refsManager


@JsonResponseWithException()
def Operations_refs_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Operations_refs.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Operations_refsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_refs_Add(request):
    return JsonResponse(DSResponseAdd(data=Operations_refs.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_refs_Update(request):
    return JsonResponse(DSResponseUpdate(data=Operations_refs.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_refs_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Operations_refs.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_refs_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Operations_refs.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_refs_Info(request):
    return JsonResponse(DSResponse(request=request, data=Operations_refs.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
