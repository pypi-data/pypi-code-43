import uuid
import json
import redis

from .param import Param
from .consul import Consul
from .command import Command
from .response import Response
from .errors import MakeRequestError, ServiceNotFoundError


class LakaClient(object):

    def __init__(self, service_name, consul_host, consul_port):
        self.consul_host = consul_host
        self.consul_port = consul_port
        self.redis_client = None
        self.service_name = service_name
        self.consul = Consul(self.consul_host, self.consul_port)
        self.service = self.consul.get_service(service_name)
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