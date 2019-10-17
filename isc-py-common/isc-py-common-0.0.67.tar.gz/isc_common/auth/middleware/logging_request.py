import json
import logging

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from history.models.history import History
from isc_common import getAttr

logger = logging.getLogger(__name__)


class LoggingRequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            bodyStr = request.body.decode("utf-8")
            self.json = json.loads(bodyStr)

        except:
            self.json = None

        if settings.EXCLUDE_REQUEST_PATHES == None:
            settings.EXCLUDE_REQUEST_PATHES = ['Info', 'Update1']

        username = getAttr(request.session._session, 'username')
        fio = getAttr(request.session._session, 'fio', 'unknown')
        if username != None:
            enable_logging = len([item for item in settings.EXCLUDE_REQUEST_PATHES if request.path.find(item) != -1]) == 0
            if enable_logging and self.json != None:
                logger.debug(f'request.path : {request.path}')
                history_element = History.objects.using('history').create(username=username, fio=fio, method=request.method, path=request.path, data=self.json)

                logger.debug('=========================================================================================================')
                logger.debug(f'date: {history_element.date}')
                logger.debug(f'username: {username}')
                logger.debug(f'method: {request.method}')
                logger.debug(f'path: {request.path}')
                logger.debug(f'json: {json.dumps(self.json, indent=4, sort_keys=True)}')
                logger.debug('=========================================================================================================\n')

    def process_response(self, request, response):
        return response
