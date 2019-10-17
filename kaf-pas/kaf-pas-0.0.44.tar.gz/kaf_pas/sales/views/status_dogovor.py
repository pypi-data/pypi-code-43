from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.sales.models.status_dogovor import StatusDogovor, StatusDogovorManager


@JsonResponseWithException()
def StatusDogovor_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=StatusDogovor.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=StatusDogovorManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def StatusDogovor_Add(request):
    return JsonResponse(DSResponseAdd(data=StatusDogovor.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def StatusDogovor_Update(request):
    return JsonResponse(DSResponseUpdate(data=StatusDogovor.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def StatusDogovor_Remove(request):
    return JsonResponse(DSResponse(request=request, data=StatusDogovor.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def StatusDogovor_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=StatusDogovor.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def StatusDogovor_Info(request):
    return JsonResponse(DSResponse(request=request, data=StatusDogovor.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def StatusDogovor_Copy(request):
    return JsonResponse(DSResponse(request=request, data=StatusDogovor.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)            
