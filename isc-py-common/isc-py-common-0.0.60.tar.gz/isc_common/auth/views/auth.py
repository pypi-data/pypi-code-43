from isc_common.auth.http.ChangePassRequest import ChangePassRequest
from isc_common.auth.http.Link2Group import Link2Group
from isc_common.auth.http.LoginRequets import LoginRequest
from isc_common.auth.http.UnLinkFromGroup import UnlinkFromGroup
from isc_common.auth.http.copyPermission import CopyPermission
from isc_common.http.DSResponse import JsonResponseWithException
from isc_common.http.response import JsonResponse


@JsonResponseWithException(printing=False)
def login(request):
    return JsonResponse(LoginRequest(request).response)


@JsonResponseWithException(printing=False)
def changepassword(request):
    return JsonResponse(ChangePassRequest(request).response)

@JsonResponseWithException(printing=False)
def link2group(request):
    return JsonResponse(Link2Group(request).response)

@JsonResponseWithException(printing=False)
def unlinkFromgroup(request):
    return JsonResponse(UnlinkFromGroup(request).response)


@JsonResponseWithException(printing=False)
def copyPermission(request):
    return JsonResponse(CopyPermission(request).response)
