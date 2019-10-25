from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.kd.models.cdw_attrs import Cdw_attrs, Cdw_attrsManager


@JsonResponseWithException()
def Cdw_attrs_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Cdw_attrs.objects.
                select_related('document', 'attr_type').
                get_range_rows1(
                request=request,
                function=Cdw_attrsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Cdw_attrs_Add(request):
    return JsonResponse(DSResponseAdd(data=Cdw_attrs.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Cdw_attrs_Update(request):
    return JsonResponse(DSResponseUpdate(data=Cdw_attrs.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Cdw_attrs_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Cdw_attrs.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Cdw_attrs_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Cdw_attrs.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Cdw_attrs_Info(request):
    return JsonResponse(DSResponse(request=request, data=Cdw_attrs.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
