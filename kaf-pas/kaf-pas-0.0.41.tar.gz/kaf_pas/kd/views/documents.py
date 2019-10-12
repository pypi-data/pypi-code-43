import logging

import requests
from django.conf import settings
from django.http import HttpResponseRedirect

from isc_common import ws
from isc_common.http.DSRequest import DSRequest
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.kd.models.documents import Documents, DocumentManager

logger = logging.getLogger(__name__)


@JsonResponseWithException()
def Documents_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Documents.objects.
                select_related('attr_type').
                get_range_rows1(
                request=request,
                function=DocumentManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_Add(request):
    return JsonResponse(DSResponseAdd(data=Documents.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_Update(request):
    return JsonResponse(DSResponseUpdate(data=Documents.objects.updateFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_Remove(request):
    ws_channel = request.session.get('ws_channel')
    ws_port = request.session.get('ws_port')
    host = ws.WS_HOST

    _request = DSRequest(request=request)
    ids = _request.get_tuple_ids()
    r = requests.get(f'{settings.KOMPAS_INFORMICA}/logic/Documents/Remove', params=dict(ids=ids, port=ws_port, ws_channel=ws_channel, host=host))
    HttpResponseRedirect(r.url)
    return JsonResponse(DSResponse(request=request, status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Documents.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_Info(request):
    return JsonResponse(DSResponse(request=request, data=Documents.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_MakeItem(request):
    from kaf_pas.ckk.models.attr_type import Attr_type
    from kaf_pas.kd.models.document_attributes import Document_attributes
    from kaf_pas.ckk.models.item import Item

    class Log:
        def logging(self, msg, mode='info'):
            if mode == 'debug':
                logger.debug(msg)
            elif mode == 'info':
                logger.info(msg)

    log = Log()

    _request = DSRequest(request=request)
    ids = _request.get_data()
    if isinstance(ids, dict):
        for id in ids.get('ids'):
            document = Documents.objects.get(id=id)
            if document.attr_type.code == 'SPW':
                top_auto_level_type, _ = Attr_type.objects.get_or_create(code='top_auto_level')

                top_auto_level_attr, _ = Document_attributes.objects.get_or_create(attr_type=top_auto_level_type, value_str='Автоматически сгененрированный состав изделий')
                top_auto_level_item, _ = Item.objects.get_or_create(STMP_1=top_auto_level_attr, props=Item.props.relevant | Item.props.from_spw)

                DocumentManager.make_spw(document=document, top_auto_level_item=top_auto_level_item, logger=log)

            elif document.attr_type.code == 'CDW':
                DocumentManager.make_cdw(document=document, logger=log)

            elif document.attr_type.code == 'KD_PDF':

                STMP_1_type = Attr_type.objects.get(code='STMP_1')
                STMP_2_type = Attr_type.objects.get(code='STMP_2')

                DocumentManager.make_pdf(document=document, STMP_1_type=STMP_1_type, STMP_2_type=STMP_2_type, logger=log)
    return JsonResponse(DSResponse(request=request, status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Documents_Treat(request):
    ws_channel = request.session.get('ws_channel')
    ws_port = request.session.get('ws_port')
    host = ws.WS_HOST

    _request = DSRequest(request=request)
    ids = _request.get_tuple_ids()
    r = requests.get(f'{settings.KOMPAS_INFORMICA}/logic/Documents/Treat', params=dict(ids=ids, port=ws_port, ws_channel=ws_channel, host=host))
    HttpResponseRedirect(r.url)
    return JsonResponse(DSResponse(request=request, status=RPCResponseConstant.statusSuccess).response)@JsonResponseWithException()


@JsonResponseWithException()
def Documents_ReloadDoc(request):
    ws_channel = request.session.get('ws_channel')
    ws_port = request.session.get('ws_port')
    host = ws.WS_HOST

    _request = DSRequest(request=request)
    ids = _request.json.get('data')
    ids = ids.get('ids')

    r = requests.get(f'{settings.KOMPAS_INFORMICA}/logic/Documents/ReloadDoc', params=dict(ids=ids, port=ws_port, ws_channel=ws_channel, host=host))
    HttpResponseRedirect(r.url)
    return JsonResponse(DSResponse(request=request, status=RPCResponseConstant.statusSuccess).response)
