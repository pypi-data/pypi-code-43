from isc_common.auth.models.user import User
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.input.models.user_view import User_view, User_viewManager


@JsonResponseWithException()
def User_view_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=User_view.objects.
                get_range_rows1(
                request=request,
                # function=User_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_view_Add(request):
    return JsonResponse(DSResponseAdd(data=User.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_view_Update(request):
    return JsonResponse(DSResponseUpdate(data=User.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_view_Remove(request):
    return JsonResponse(DSResponse(request=request, data=User.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_view_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=User.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_view_Info(request):
    return JsonResponse(DSResponse(request=request, data=User.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
