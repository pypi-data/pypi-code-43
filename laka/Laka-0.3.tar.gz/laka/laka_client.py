import uuid
import json
import redis

from .fofo import Fofo
from .param import Param
from .command import Command
from .response import Response
from .laka_service import LakaService
from .errors import MakeRequestError, ServiceNotFoundError


class LakaClient(object):

    def __init__(self, service_name, fofo_host, fofo_port):
        self.fofo_host = fofo_host
        self.fofo_port = fofo_port
        self.redis_client = None
        self.service_name = service_name
        self.fofo = Fofo(self.fofo_host, self.fofo_port)
        self.service_list = self.fofo.search_service(name=service_name)
        self.service = self.service_list[0] if self.service_list else None
        self.service = LakaService.load_from_json(self.service)
        if not self.service:
            raise ServiceNotFoundError("service {} not found".format(service_name))
        self._connect_redis()
    
    def _connect_redis(self):
        self.redis_client = redis.Redis(host=self.service.redis_host, port=self.service.redis_port, db=self.service.redis_db)
    
    def request(self, code, param):
        if not isinstance(param, Param):
            raise MakeRequestError("param should an object of Param")
        request_id = self.new_request_id()
        cmd = Command(code, param, request_id)
        try:
            r = json.dumps(cmd.json())
        except Exception as e:
            raise MakeRequestError(e)
        self.redis_client.lpush(self.service.queue, r)
        return request_id
    
    def _accept(self, queue):
        d = self.redis_client.brpop(queue)
        try:
            data = json.loads(str(d[1], encoding="utf8"))
        except Exception as e:
            raise InvalidMessage(e)
        return data
    
    def accept_response(self, request_id):
        data = self._accept(request_id)
        response = Response.load_from_dict(data)
        return response

    @staticmethod
    def new_request_id():
        return "LAKA:REQUEST_ID:{}".format(uuid.uuid4().hex)