from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse

from kaf_pas.kd.models.documents_thumb10 import Documents_thumb10


@JsonResponseWithException()
def Documents_thumb10_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Documents_thumb10.objects.
                select_related().
                get_range_rows1(
                request=request,
                # function=XXX.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_thumb10_Add(request):
    return JsonResponse(DSResponseAdd(data=Documents_thumb10.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_thumb10_Update(request):
    return JsonResponse(DSResponseUpdate(data=Documents_thumb10.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_thumb10_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Documents_thumb10.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_thumb10_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Documents_thumb10.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_thumb10_Info(request):
    return JsonResponse(DSResponse(request=request, data=Documents_thumb10.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
