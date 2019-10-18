from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.planing.models.operations_plan_qtys import Operations_plan_qtys


class Operations_plan_qtysManager(object):
    pass


@JsonResponseWithException()
def Operations_plan_qtys_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Operations_plan_qtys.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Operations_plan_qtysManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_plan_qtys_Add(request):
    return JsonResponse(DSResponseAdd(data=Operations_plan_qtys.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_plan_qtys_Update(request):
    return JsonResponse(DSResponseUpdate(data=Operations_plan_qtys.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_plan_qtys_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Operations_plan_qtys.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_plan_qtys_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Operations_plan_qtys.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_plan_qtys_Info(request):
    return JsonResponse(DSResponse(request=request, data=Operations_plan_qtys.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_plan_qtys_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Operations_plan_qtys.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
