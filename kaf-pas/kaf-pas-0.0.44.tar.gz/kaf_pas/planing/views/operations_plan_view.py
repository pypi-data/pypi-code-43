from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.planing.models.operations_plan_view import Operations_plan_viewManager, Operations_plan_view


@JsonResponseWithException()
def Operations_plan_view_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Operations_plan_view.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Operations_plan_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_plan_view_Add(request):
    return JsonResponse(DSResponseAdd(data=Operations_plan_view.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_plan_view_Update(request):
    return JsonResponse(DSResponseUpdate(data=Operations_plan_view.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_plan_view_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Operations_plan_view.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_plan_view_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Operations_plan_view.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_plan_view_Info(request):
    return JsonResponse(DSResponse(request=request, data=Operations_plan_view.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_plan_view_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Operations_plan_view.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)            
