import uuid
import json
import redis

from .fofo import Fofo
from .param import Param
from .command import Command
from .response import Response
from .laka_service import LakaService
from .handler import Handler, HandlerOK, HandlerFailed
from .errors import InvalidHandler, HandlerNotFound, InvalidMessage, MakeRequestError, RegisterServiceFailed


class LakaServer(object):

    def __init__(self, service_name, redis_host, redis_port, redis_queue, fofo_host, fofo_port, response_message=None, redis_db=0, check_health=False):
        self.service_name = service_name
        self.fofo_host = fofo_host
        self.fofo_port = fofo_port
        self.redis_client = None
        if response_message and not isinstance(response_message, dict):
            raise TypeError("Invalid type of response_message, dict is expected but {} found".format(type(response_message)))
        self.response_message = response_message if response_message else {}
        self.service = LakaService(service_name, redis_host, redis_port, redis_queue, redis_db)
        self.handlers = {}
        self._connect_redis()
        self.fofo = Fofo(self.fofo_host, self.fofo_port)
        self.fofo.register_service(self.service)
        if check_health:
            self.fofo.health_check()

    def _connect_redis(self):
        self.redis_client = redis.Redis(host=self.service.redis_host, port=self.service.redis_port, db=self.service.redis_db)
    
    def router(self, command_code, handler):
        if not issubclass(handler, Handler):
            raise InvalidHandler("handler should be subclass of Handler, but {} found".format(handler))
        if handler.Param and not issubclass(handler.Param, Param):
            raise InvalidHandler("handler.Param should be subclass of Param, but {} found".format(handler.Param))
        self.handlers[command_code] = handler

    def handle(self, cmd):
        handler = self.handlers.get(cmd.code)
        if not handler:
            raise HandlerNotFound("handler not found for CommandCode = {}".format(cmd.code))
        h = handler()
        h.get_param(cmd)
        return h.handle()

    def _accept(self, queue):
        d = self.redis_client.brpop(queue)
        try:
            data = json.loads(str(d[1], encoding="utf8"))
        except Exception as e:
            raise InvalidMessage(e)
        return str(d[0]), data
    
    def accept_request(self):
        while True:
            queue, data = self._accept(self.service.queue)
            if not data:
                continue
            cmd = Command.load_from_dict(data)
            yield queue, cmd

    def response(self, request_id, handler_response):
        """
        由于发送返回数据时，需要知道 request_id，因此如果请求时数据格式不正确或者缺少 request_id，则该请求将得不到任何返回值。
        所以必须确保发送请求时数据格式正确。
        """
        if not isinstance(handler_response, (HandlerFailed, HandlerOK)):
            raise MakeResponseError("the type of handler_response should be HandlerOK or HandlerFailed, but {} found".format(type(handler_response)))
        message = self.response_message.get(handler_response.code)
        resp = Response(request_id, handler_response.code, handler_response.data, message)
        try:
            data = json.dumps(resp.json())
        except Exception as e:
            raise MakeResponseError(e)
        self.redis_client.lpush(request_id, data)
    
    # @staticmethod
    # def get_heartbeat_queue(service_name):
    #     return "LAKA:HEARTBEAT:{}".format(service_name)

