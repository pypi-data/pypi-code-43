import requests
from django.conf import settings
from django.http import HttpResponseRedirect

from isc_common import ws
from isc_common.http.DSRequest import DSRequest
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.kd.models.documents import Documents
from kaf_pas.kd.models.documents_mview import Documents_mview
from kaf_pas.kd.models.documents_view import Documents_view


@JsonResponseWithException()
def Documents_view_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Documents_view.objects.
                select_related().
                filter(attr_type__code__in=['KD_PDF', 'CDW', 'SPW']).
                get_range_rows1(
                request=request,
                function=Documents_view.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_bad_view_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Documents_view.objects.
                select_related('STMP_1','STMP_2').
                filter(attr_type__code__in=['KD_BAD']).
                get_range_rows1(
                request=request,
                function=Documents_view.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_view_Add(request):
    return JsonResponse(DSResponseAdd(data=Documents.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_view_Update(request):
    return JsonResponse(DSResponseUpdate(data=Documents.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_view_Remove(request):
    ws_channel = request.session.get('ws_channel')
    ws_port = settings.WS_PORT
    host = settings.WS_HOST

    _request = DSRequest(request=request)
    ids = _request.get_tuple_ids()
    r = requests.get(f'{settings.KOMPAS_INFORMICA}/logic/Documents/Remove', params=dict(ids=ids, port=ws_port, ws_channel=ws_channel, host=host))
    HttpResponseRedirect(r.url)
    return JsonResponse(DSResponse(request=request, status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_view_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Documents.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_view_Info(request):
    return JsonResponse(DSResponse(request=request, data=Documents_view.objects.select_related('STMP_1','STMP_2').get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_view_bad_Info(request):
    return JsonResponse(DSResponse(request=request, data=Documents_mview.objects.select_related('STMP_1','STMP_2').filter(attr_type__code__in=['KD_BAD']).get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
