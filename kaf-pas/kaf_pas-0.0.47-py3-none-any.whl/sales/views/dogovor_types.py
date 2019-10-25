from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.sales.models.dogovor_types import Dogovor_types, Dogovor_typesManager


@JsonResponseWithException()
def Dogovor_types_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Dogovor_types.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Dogovor_typesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Dogovor_types_Add(request):
    return JsonResponse(DSResponseAdd(data=Dogovor_types.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Dogovor_types_Update(request):
    return JsonResponse(DSResponseUpdate(data=Dogovor_types.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Dogovor_types_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Dogovor_types.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Dogovor_types_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Dogovor_types.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Dogovor_types_Info(request):
    return JsonResponse(DSResponse(request=request, data=Dogovor_types.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Dogovor_types_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Dogovor_types.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)            
