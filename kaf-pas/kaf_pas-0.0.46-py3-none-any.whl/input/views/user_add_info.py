from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.input.models.user_add_info import User_add_infoManager, User_add_info


@JsonResponseWithException()
def User_add_info_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=User_add_info.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=User_add_infoManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_add_info_Add(request):
    return JsonResponse(DSResponseAdd(data=User_add_info.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_add_info_Update(request):
    return JsonResponse(DSResponseUpdate(data=User_add_info.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_add_info_Remove(request):
    return JsonResponse(DSResponse(request=request, data=User_add_info.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_add_info_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=User_add_info.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_add_info_Info(request):
    return JsonResponse(DSResponse(request=request, data=User_add_info.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
