from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.kd.models.document_attr_cross import Document_attr_cross


@JsonResponseWithException()
def Document_attr_cross_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Document_attr_cross.objects.
                select_related().
                get_range_rows1(
                request=request,
                # function=Document_attr_crossManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Document_attr_cross_Add(request):
    return JsonResponse(DSResponseAdd(data=Document_attr_cross.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Document_attr_cross_Update(request):
    return JsonResponse(DSResponseUpdate(data=Document_attr_cross.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Document_attr_cross_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Document_attr_cross.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Document_attr_cross_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Document_attr_cross.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Document_attr_cross_Info(request):
    return JsonResponse(DSResponse(request=request, data=Document_attr_cross.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)    
