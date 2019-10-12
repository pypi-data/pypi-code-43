import requests
from django.conf import settings
from django.http import HttpResponseRedirect

from isc_common import ws
from isc_common.http.DSRequest import DSRequest
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException, JsonWSResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.kd.models.documents_thumb import Documents_thumb, Documents_thumbManager


@JsonResponseWithException()
def Documents_thumb_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Documents_thumb.objects.
                select_related('document').
                get_range_rows1(
                request=request,
                function=Documents_thumbManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_thumb_Add(request):
    return JsonResponse(DSResponseAdd(data=Documents_thumb.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_thumb_Update(request):
    return JsonResponse(DSResponseUpdate(data=Documents_thumb.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonWSResponseWithException()
def Documents_thumb_Remove(request):
    ws_channel = request.session.get('ws_channel')
    ws_port = request.session.get('ws_port')
    host = ws.WS_HOST

    _request = DSRequest(request=request)

    _transaction = _request.json.get('transaction')
    ids = []
    if _transaction:
        for operation in _transaction.get('operations'):
            data = operation.get('data')
            for id in data.get('ids'):
                ids.append((id, None))
    else:
        data = _request.json.get('data')
        for id in data.get('ids'):
            ids.append((id, None))

    for id in ids:
        from kaf_pas.ckk.models.item_image_refs import Item_image_refs
        from kaf_pas.kd.models.documents_thumb10 import Documents_thumb10

        thumb = Documents_thumb.objects.get(id=id[0])
        for thumb10 in Documents_thumb10.objects.filter(path=thumb.path):
            Item_image_refs.objects.filter(thumb10=thumb10).delete()

        Item_image_refs.objects.filter(thumb=thumb).delete()

    r = requests.get(f'{settings.KOMPAS_INFORMICA}/logic/DocumentsThumb/Remove', params=dict(ids=ids, port=ws_port, ws_channel=ws_channel, host=host))
    HttpResponseRedirect(r.url)
    return JsonResponse(DSResponse(request=request, status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_thumb_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Documents_thumb.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_thumb_Info(request):
    return JsonResponse(DSResponse(request=request, data=Documents_thumb.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
