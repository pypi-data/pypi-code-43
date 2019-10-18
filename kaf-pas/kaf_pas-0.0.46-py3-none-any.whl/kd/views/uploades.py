import requests
from django.conf import settings
from django.http import HttpResponseRedirect

from isc_common import ws
from isc_common.http.DSRequest import DSRequest
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.kd.models.uploades import Uploades, UploadesManager


@JsonResponseWithException()
def Uploades_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Uploades.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=UploadesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Uploades_Add(request):
    return JsonResponse(DSResponseAdd(data=Uploades.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Uploades_Update(request):
    return JsonResponse(DSResponseUpdate(data=Uploades.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Uploades_Remove(request):
    ws_channel = request.session.get('ws_channel')
    ws_port = settings.WS_PORT
    host = settings.WS_HOST

    _request = DSRequest(request=request)
    ids = _request.get_tuple_ids()
    r = requests.get(f'{settings.KOMPAS_INFORMICA}/logic/Uploades/Remove', params=dict(ids=ids, port=ws_port, ws_channel=ws_channel, host=host))
    HttpResponseRedirect(r.url)
    return JsonResponse(DSResponse(request=request, status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Uploades_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Uploades.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Uploades_Info(request):
    return JsonResponse(DSResponse(request=request, data=Uploades.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Uploades_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Uploades.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
