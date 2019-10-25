from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.sales.models.precent_item_types import Precent_item_typesManager, Precent_item_types


@JsonResponseWithException()
def Precent_item_types_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Precent_item_types.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Precent_item_typesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_item_types_Add(request):
    return JsonResponse(DSResponseAdd(data=Precent_item_types.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_item_types_Update(request):
    return JsonResponse(DSResponseUpdate(data=Precent_item_types.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_item_types_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Precent_item_types.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_item_types_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Precent_item_types.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_item_types_Info(request):
    return JsonResponse(DSResponse(request=request, data=Precent_item_types.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_item_types_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Precent_item_types.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)            
