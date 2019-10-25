from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.sales.models.precent_dogovors import Precent_dogovors, Precent_dogovorsManager


@JsonResponseWithException()
def Precent_dogovors_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Precent_dogovors.objects.
                select_related('dogovor', 'precent').
                get_range_rows1(
                request=request,
                function=Precent_dogovorsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_dogovors_Add(request):
    return JsonResponse(DSResponseAdd(data=Precent_dogovors.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_dogovors_Update(request):
    return JsonResponse(DSResponseUpdate(data=Precent_dogovors.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_dogovors_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Precent_dogovors.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_dogovors_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Precent_dogovors.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_dogovors_Info(request):
    return JsonResponse(DSResponse(request=request, data=Precent_dogovors.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_dogovors_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Precent_dogovors.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
