import json
import logging
import math
import pprint
import sys
import traceback

from django.conf import settings
from django.db.models import QuerySet, Model
from django.forms import model_to_dict
from websocket import create_connection

from isc_common import setAttr
from isc_common.common.functions import Common
from isc_common.http.DSRequest import RequestData, DSRequest
from isc_common.http.RPCResponse import RPCResponse, RPCResponseConstant
from isc_common.http.response import JsonResponse

logger = logging.getLogger(__name__)


def JsonResponseWithException(printing=False, printing_res=False):
    class JE:
        def __init__(self, func):
            self.func = func
            self.pp = pprint.PrettyPrinter(indent=4)

        def print(self, o, str=None):
            if str:
                print(f"=========== Begin {str} ========================")
            else:
                print(f"=========== Begin {o.__class__.__name__} ========================")
            if isinstance(o, dict):
                self.pp.pprint(RequestData(o).getDataWithOutField(['pp', '_state']).dict())
            elif isinstance(o, object):
                self.pp.pprint(RequestData(o.__dict__).getDataWithOutField(['pp', '_state']).dict())

            if str:
                print(f"=========== End   {str} ========================")
            else:
                print(f"=========== End   {o.__class__.__name__} ========================")
            print("\n")

        def __call__(self, *args, **kwargs):
            try:
                if printing:
                    request = args[0]
                    _request = DSRequest(request)
                    self.print(_request)
                    self.print(request.COOKIES, 'request.COOKIES')
                    self.print(request.GET, 'request.GET')
                    self.print(request.POST, 'request.POST')
                    self.print(request.META, 'request.META')

                res = self.func(*args, **kwargs)
                if printing_res:
                    self.print(res)
                return res
            except Exception as ex:
                exc_info = sys.exc_info()
                stackTrace = traceback.format_exception(*exc_info)
                message = str(ex)
                for x in stackTrace:
                    logger.error(x)

                del exc_info

                return JsonResponse(DSResponseFailure(message=message, stackTrace=stackTrace).response)

    return JE

def JsonWSResponseWithException(printing=False, printing_res=False):
    class JE:
        def __init__(self, func):
            self.func = func
            self.pp = pprint.PrettyPrinter(indent=4)

        def print(self, o, str=None):
            if str:
                print(f"=========== Begin {str} ========================")
            else:
                print(f"=========== Begin {o.__class__.__name__} ========================")
            if isinstance(o, dict):
                self.pp.pprint(RequestData(o).getDataWithOutField(['pp', '_state']).dict())
            elif isinstance(o, object):
                self.pp.pprint(RequestData(o.__dict__).getDataWithOutField(['pp', '_state']).dict())

            if str:
                print(f"=========== End   {str} ========================")
            else:
                print(f"=========== End   {o.__class__.__name__} ========================")
            print("\n")

        def __call__(self, *args, **kwargs):
            request = args[0]

            self.port = request.GET.get('ws_port')
            if not self.port:
                self.port = request.GET.get('port')
                if not self.port:
                    self.port = request.session._session.get('ws_port')
                    if not self.port:
                        self.port = settings.WS_PORT
                        if not self.port:
                            raise Exception(Common.arraund_error('Do not have ws_port'))

            self.host = request.GET.get('ws_host')
            if not self.host:
                self.host = request.GET.get('host')
                if not self.host:
                    self.host = request.session._session.get('host')
                    if not self.host:
                        self.host = settings.WS_HOST
                        if not self.host:
                            raise Exception(Common.arraund_error('Do not have ws_host'))

            self.channel = request.GET.get('ws_channel')
            if not self.channel:
                self.channel = request.session._session.get('ws_channel')
                if not self.channel:
                    raise Exception(Common.arraund_error('Do not have ws_channel'))

            try:
                if printing:
                    _request = DSRequest(request)
                    self.print(_request)
                    self.print(request.COOKIES, 'request.COOKIES')
                    self.print(request.GET, 'request.GET')
                    self.print(request.POST, 'request.POST')
                    self.print(request.META, 'request.META')

                res = self.func(*args, **kwargs)
                if printing_res:
                    self.print(res)

                return res
            except Exception as ex:
                exc_info = sys.exc_info()
                stackTrace = traceback.format_exception(*exc_info)
                message = str(ex)

                try:
                    ws = create_connection(f"ws://{self.host}:{self.port}/ws/{self.channel}/")
                    ws.send(json.dumps(dict(message=message, stackTrace=stackTrace, type="error")))
                    ws.close()
                except Exception as ex:

                    exc_info = sys.exc_info()
                    message = str(ex)
                    stackTrace = traceback.format_exception(*exc_info)

                    logging.error(message)

                    for x in stackTrace:
                        logger.error(x)

                    del exc_info

                for x in stackTrace:
                    logger.error(x)

                return JsonResponse(DSResponseOk().response)

    return JE

def JsonWSPostResponseWithException(printing=False, printing_res=False):
    class JE:
        def __init__(self, func):
            self.func = func
            self.pp = pprint.PrettyPrinter(indent=4)

        def print(self, o, str=None):
            if str:
                print(f"=========== Begin {str} ========================")
            else:
                print(f"=========== Begin {o.__class__.__name__} ========================")
            if isinstance(o, dict):
                self.pp.pprint(RequestData(o).getDataWithOutField(['pp', '_state']).dict())
            elif isinstance(o, object):
                self.pp.pprint(RequestData(o.__dict__).getDataWithOutField(['pp', '_state']).dict())

            if str:
                print(f"=========== End   {str} ========================")
            else:
                print(f"=========== End   {o.__class__.__name__} ========================")
            print("\n")

        def __call__(self, *args, **kwargs):
            request = args[0]

            self.port = request.POST.get('ws_port')
            if not self.port:
                self.port = request.session._session.get('ws_port')
                if not self.port:
                    raise Exception(Common.arraund_error('Do not have ws_port'))

            self.host = request.POST.get('ws_host')
            if not self.host:
                self.host = request.session._session.get('host')
                if not self.host:
                    raise Exception(Common.arraund_error('Do not have ws_host'))

            self.channel = request.POST.get('ws_channel')
            if not self.channel:
                self.channel = request.session._session.get('ws_channel')
                if not self.channel:
                    raise Exception(Common.arraund_error('Do not have ws_channel'))

            try:
                if printing:
                    _request = DSRequest(request)
                    self.print(_request)
                    self.print(request.COOKIES, 'request.COOKIES')
                    self.print(request.GET, 'request.GET')
                    self.print(request.POST, 'request.POST')
                    self.print(request.META, 'request.META')

                res = self.func(*args, **kwargs)
                if printing_res:
                    self.print(res)

                return res
            except Exception as ex:
                exc_info = sys.exc_info()
                stackTrace = traceback.format_exception(*exc_info)
                message = str(ex)

                try:
                    ws = create_connection(f"ws://{self.host}:{self.port}/ws/{self.channel}/")
                    ws.send(json.dumps(dict(message=message, stackTrace=stackTrace, type="error")))
                    ws.close()
                except Exception as ex:

                    exc_info = sys.exc_info()
                    message = str(ex)
                    stackTrace = traceback.format_exception(*exc_info)

                    logging.error(message)

                    for x in stackTrace:
                        logger.error(x)

                    del exc_info

                for x in stackTrace:
                    logger.error(x)

                return JsonResponse(DSResponseOk().response)

    return JE


class DSResponse(RPCResponse):

    def normal_round(self, n):
        if n - math.floor(n) < 0.5:
            return math.floor(n)
        return math.ceil(n)

    def __init__(self,
                 request,
                 clientContext=None,
                 data=None,
                 message=None,
                 stackTrace=None,
                 httpHeaders=None,
                 httpResponseCode=None,
                 httpResponseText=None,
                 status=RPCResponseConstant.statusSuccess,
                 transactionNum=None,
                 dataSource=None,
                 errors=None,
                 invalidateCache=None,
                 operationId=None,
                 operationType=None,
                 queueStatus=None,
                 totalRows=None
                 ):
        RPCResponse.__init__(self,
                             clientContext=clientContext,
                             data=data,
                             httpHeaders=httpHeaders,
                             httpResponseCode=httpResponseCode,
                             httpResponseText=httpResponseText,
                             status=status,
                             transactionNum=transactionNum)

        request = DSRequest(request=request) if request else None
        self.dataSource = dataSource
        self.endRow = request.endRow if request else None
        self.startRow = request.startRow if request else None
        self.drawAheadRatio = request.drawAheadRatio if request else 1.2
        self.errors = errors
        self.invalidateCache = invalidateCache
        self.operationId = operationId
        self.operationType = operationType
        self.queueStatus = queueStatus

        self.message = message
        self.stackTrace = stackTrace
        self.status = status

        if isinstance(data, QuerySet):
            data = list(data)

        if isinstance(data, list):

            if self.startRow is not None and self.endRow is not None :
                qty = self.endRow - self.startRow
                len_data = len(self.data)

                if len_data == 0:
                    self.totalRows = 0
                else:
                    if len_data == qty:
                        self.totalRows = self.startRow + self.normal_round(qty * self.drawAheadRatio)
                    else:
                        self.totalRows = self.startRow + len_data

                # logger.debug(f'startRow: {self.startRow}, endRow: {self.endRow}, qty: {qty}, len_data: {len_data}, totalRows: {self.totalRows}')
            else:
                self.totalRows = totalRows
        else:
            self.totalRows = totalRows

    @property
    def response(self):
        setAttr(self.dict,'startRow', self.startRow)
        setAttr(self.dict,'endRow', self.endRow)
        setAttr(self.dict,'totalRows', self.totalRows)
        # logger.debug(f'self.dict: {self.dict}')
        return dict(response=self.dict)


class DSResponseAdd(DSResponse):
    def __init__(self, data, status):
        if isinstance(data, Model):
            data = [model_to_dict(data)]

        DSResponse.__init__(self,
                            request=None,
                            clientContext=None,
                            data=data,
                            httpHeaders=None,
                            httpResponseCode=None,
                            httpResponseText=None,
                            status=status,
                            transactionNum=None,
                            dataSource=None,
                            errors=None,
                            invalidateCache=None,
                            operationId=None,
                            operationType=None,
                            queueStatus=None,
                            totalRows=None,
                            )


class DSResponseCopy(DSResponse):
    def __init__(self, data, status):
        if isinstance(data, Model):
            data = [model_to_dict(data)]

        DSResponse.__init__(self,
                            request=None,
                            clientContext=None,
                            data=data,
                            httpHeaders=None,
                            httpResponseCode=None,
                            httpResponseText=None,
                            status=status,
                            transactionNum=None,
                            dataSource=None,
                            errors=None,
                            invalidateCache=None,
                            operationId=None,
                            operationType=None,
                            queueStatus=None,
                            totalRows=None,
                            )


class DSResponseUpdate(DSResponse):
    def __init__(self, data, status):
        if isinstance(data, Model):
            data = [model_to_dict(data)]

        DSResponse.__init__(self,
                            request=None,
                            clientContext=None,
                            data=data,
                            httpHeaders=None,
                            httpResponseCode=None,
                            httpResponseText=None,
                            status=status,
                            transactionNum=None,
                            dataSource=None,
                            errors=None,
                            invalidateCache=None,
                            operationId=None,
                            operationType=None,
                            queueStatus=None,
                            totalRows=None,
                            )

        @property
        def response(self):
            return dict(response=dict(status=self.status, data=self.data))


class DSResponseLookup(DSResponse):
    def __init__(self, data, status):
        if isinstance(data, Model):
            data = [model_to_dict(data)]

        DSResponse.__init__(self,
                            request=None,
                            clientContext=None,
                            data=data,
                            httpHeaders=None,
                            httpResponseCode=None,
                            httpResponseText=None,
                            status=status,
                            transactionNum=None,
                            dataSource=None,
                            errors=None,
                            invalidateCache=None,
                            operationId=None,
                            operationType=None,
                            queueStatus=None,
                            totalRows=None,
                            )

        @property
        def response(self):
            return dict(response=dict(status=self.status, data=self.data))


class DSResponseOk(DSResponse):
    def __init__(self):
        DSResponse.__init__(self,
                            request=None,
                            clientContext=None,
                            data=[],
                            httpHeaders=None,
                            httpResponseCode=None,
                            httpResponseText=None,
                            status=RPCResponseConstant.statusSuccess,
                            transactionNum=None,
                            dataSource=None,
                            errors=None,
                            invalidateCache=None,
                            operationId=None,
                            operationType=None,
                            queueStatus=None,
                            totalRows=None,
                            )

    @property
    def response(self):
        return dict(response=dict(status=self.status))


class DSResponseFailure(DSResponse):
    def __init__(self,
                 message=None,
                 stackTrace=None
                 ):
        DSResponse.__init__(self,
                            request=None,
                            clientContext=None,
                            message=message,
                            stackTrace=stackTrace,
                            httpHeaders=None,
                            httpResponseCode=None,
                            httpResponseText=None,
                            status=RPCResponseConstant.statusFailure,
                            transactionNum=None,
                            dataSource=None,
                            errors=None,
                            invalidateCache=None,
                            operationId=None,
                            operationType=None,
                            queueStatus=None,
                            totalRows=None,
                            )

    @property
    def response(self):
        return dict(response=dict(
            status=-1,
            data=dict(
                error=dict(
                    message=self.message,
                    stackTrace=self.stackTrace
                )
            )
        ))
