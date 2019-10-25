from isc_common.http.DSResponse import JsonResponseWithException, DSResponse, DSResponseAdd, DSResponseUpdate
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse

from kaf_pas.ckk.models.attr_type import Attr_type, AttrManager


@JsonResponseWithException()
def Attr_type_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Attr_type.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=AttrManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Attr_type_Add(request):
    return JsonResponse(DSResponseAdd(data=Attr_type.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Attr_type_Update(request):
    return JsonResponse(DSResponseUpdate(data=Attr_type.objects.updateFromRequest(request, removed=['isFolder']), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Attr_type_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Attr_type.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Attr_type_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Attr_type.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Attr_type_Info(request):
    return JsonResponse(DSResponse(request=request, data=Attr_type.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
