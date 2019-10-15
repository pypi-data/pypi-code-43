from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.kd.models.spw_attrs import Spw_attrs, Spw_attrsManager


@JsonResponseWithException()
def Spw_attrs_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Spw_attrs.objects.
                select_related('document', 'attr_type').
                get_range_rows1(
                request=request,
                function=Spw_attrsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)

@JsonResponseWithException()
def Spw_attrs_Update(request):
    return JsonResponse(DSResponseUpdate(data=Spw_attrs.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


# @JsonResponseWithException()
# def Spw_attrs_Remove(request):
#     return JsonResponse(DSResponse(request=request, data=Spw_attrs.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Spw_attrs_Info(request):
    return JsonResponse(DSResponse(request=request, data=Spw_attrs.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)

