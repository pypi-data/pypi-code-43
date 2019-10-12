import logging

import requests
from django.conf import settings
from django.http import HttpResponseRedirect

from isc_common import ws

logger = logging.getLogger(__name__)


def download_attach_file(request, id):
    ws_channel = request.session.get('ws_channel')
    ws_port = request.session.get('ws_port')
    ws_host = ws.WS_HOST

    r = requests.get(f'{settings.KOMPAS_INFORMICA}/logic/DocumentsThumb/Download/{id}/', params=dict(ws_port=ws_port, ws_channel=ws_channel, ws_host=ws_host))
    logger.debug(f'DocumentsThumb url: {r.url}')
    return HttpResponseRedirect(r.url)
    #return HttpResponseRedirect(f'{settings.KOMPAS_INFORMICA}/logic/DocumentsThumb/Download/{id}/')


def download_attach_file_10(request, id):
    ws_channel = request.session.get('ws_channel')
    ws_port = request.session.get('ws_port')
    ws_host = ws.WS_HOST

    r = requests.get(f'{settings.KOMPAS_INFORMICA}/logic/DocumentsThumb/Download10/{id}/', params=dict(ws_port=ws_port, ws_channel=ws_channel, ws_host=ws_host))
    logger.debug(f'DocumentsThumb10 url: {r.url}')
    return HttpResponseRedirect(r.url)
    #return HttpResponseRedirect(f'{settings.KOMPAS_INFORMICA}/logic/DocumentsThumb10/Download/{id}/')
