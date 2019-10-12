from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.input.models.user_positions import User_positionsManager, User_positions


@JsonResponseWithException()
def User_positions_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=User_positions.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=User_positionsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_positions_Add(request):
    return JsonResponse(DSResponseAdd(data=User_positions.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_positions_Update(request):
    return JsonResponse(DSResponseUpdate(data=User_positions.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_positions_Remove(request):
    return JsonResponse(DSResponse(request=request, data=User_positions.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_positions_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=User_positions.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_positions_Info(request):
    return JsonResponse(DSResponse(request=request, data=User_positions.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
