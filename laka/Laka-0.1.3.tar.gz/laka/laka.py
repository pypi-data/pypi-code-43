import uuid
import json
import redis

from .param import Param
from .command import Command
from .response import Response
from .handler import Handler, HandlerOK, HandlerFailed
from .errors import InvalidHandler, HandlerNotFound, InvalidMessage


class Laka(object):
    """
    Laka is a json rpc client, based on redis queue.
    """

    def __init__(self, redis_host, redis_port, redis_queue, response_message=None, redis_db=0):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.request_queue = redis_queue
        self.redis_client = None
        if response_message and not isinstance(response_message, dict):
            raise TypeError("Invalid type of response_message, dict is expected but {} found".format(type(response_message)))
        self._connect_redis()
        self.response_message = response_message if response_message else {}
        self.handlers = {}

    def _connect_redis(self):
        self.redis_client = redis.Redis(host=self.redis_host, port=self.redis_port, db=self.redis_db)
    
    def register(self, handler):
        if not issubclass(handler, Handler):
            raise InvalidHandler("handler should be subclass of Handler, but {} found".format(handler))
        if handler.CommandCode is None:
            raise InvalidHandler("CommandCode of handler should not be None")
        if handler.Param and not issubclass(handler.Param, Param):
            raise InvalidHandler("handler.Param should be subclass of Param, but {} found".format(handler.Param))
        self.handlers[handler.CommandCode] = handler

    def handle(self, cmd):
        handler = self.handlers.get(cmd.code)
        if not handler:
            raise HandlerNotFound("handler not found for CommandCode = {}".format(cmd.code))
        h = handler()
        h.get_param(cmd)
        return handler.handle(cmd)

    def request(self, code, data):
        request_id = self.new_request_id()
        cmd = Command(code, data, request_id)
        r = json.dumps(cmd.json())
        self.redis_client.lpush(self.request_queue, r)
        return request_id

    def _accept(self, queue):
        d = self.redis_client.brpop(queue)
        try:
            data = json.loads(str(d[1], encoding="utf8"))
        except Exception as e:
            raise InvalidMessage(e)
            return None
        return data
    
    def accept_request(self):
        while True:
            data = self._accept(self.request_queue)
            if not data:
                continue
            cmd = Command.load_from_dict(data)
            yield cmd
        
    def accept_response(self, request_id):
        data = self._accept(request_id)
        response = Response.load_from_dict(data)
        return response

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

    def new_request_id(self):
        return "LAKA:REQUEST_ID:{}".format(uuid.uuid4().hex)