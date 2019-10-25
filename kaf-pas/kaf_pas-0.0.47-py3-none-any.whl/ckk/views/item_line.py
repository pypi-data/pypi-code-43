from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.ckk.models.item_line import Item_line
from kaf_pas.ckk.models.item_line_view import Item_line_view, Item_line_viewManager


@JsonResponseWithException()
def Item_line_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Item_line_view.objects.
                select_related(
                'SPC_CLM_FORMAT',
                'SPC_CLM_ZONE',
                'SPC_CLM_POS',
                'SPC_CLM_MARK',
                'SPC_CLM_NAME',
                'SPC_CLM_COUNT',
                'SPC_CLM_NOTE',
                'SPC_CLM_MASSA',
                'SPC_CLM_MATERIAL',
                'SPC_CLM_USER',
                'SPC_CLM_KOD',
                'SPC_CLM_FACTORY', ).
                get_range_rows1(
                request=request,
                function=Item_line_viewManager.getRecord,
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_line_Add(request):
    return JsonResponse(DSResponseAdd(data=Item_line.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_line_Update(request):
    return JsonResponse(DSResponseUpdate(data=Item_line.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_line_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Item_line.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_line_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Item_line.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_line_Info(request):
    return JsonResponse(DSResponse(request=request, data=Item_line.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)

# @JsonResponseWithException()
# def Item_line_Copy(request):
#     return JsonResponse(DSResponse(request=request, data=Item_line.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
