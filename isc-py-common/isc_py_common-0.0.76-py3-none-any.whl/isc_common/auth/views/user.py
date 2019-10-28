from isc_common.auth.managers.user_manager import UserManager
from isc_common.auth.models.user import User
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse


@JsonResponseWithException(printing=False)
def User_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=User.objects.
                filter().
                distinct().
                get_range_rows11(
                request=request,
                function=UserManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException(printing=False)
def User_FetchExclBots(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=User.objects.
                exclude(props=User.props.bot).
                distinct().
                get_range_rows11(
                request=request,
                function=UserManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_Add(request):
    return JsonResponse(DSResponseAdd(data=User.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException(printing=False)
def User_Update(request):
    return JsonResponse(DSResponseUpdate(data=User.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_Remove(request):
    return JsonResponse(DSResponse(request=request, data=User.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def  User_Lookup(request):
    return JsonResponse(DSResponse(request=request, data= User.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_Info(request):
    return JsonResponse(DSResponse(request=request, data=User.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
