import uuid
import json
import copy
import time
import redis
import threading

from .laka_service import LakaService


FOFO_REQUEST_QUEUE = "FOFO:REQUEST"
FOFO_HEALTHCHECK_CHANNEL = "FOFO:HEALTHCHECK"
COMMAND_REGISTER_SERVICE = 100
COMMAND_GET_SERVICE = 101
COMMAND_SEARCH_SERVICE = 102
COMMAND_HEALTH_CHECK_RESPONSE = 0


class FofoCommand(object):

    def __init__(self, code, request_id, args=None):
        self.code = code
        self.args = args
        self.request_id = request_id

    @classmethod
    def New(cls, code, args):
        request_id = uuid.uuid4().hex
        return cls(code, request_id, args)
    
    def json(self):
        return copy.deepcopy(self.__dict__)


class Fofo(object):

    def __init__(self, redis_host, redis_port, redis_db=0):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self._connect_redis()

    def _connect_redis(self):
        self.redis_client = redis.Redis(host=self.redis_host, port=self.redis_port, db=self.redis_db)
    
    def _send_command(self, cmd):
        self.redis_client.lpush(FOFO_REQUEST_QUEUE, json.dumps(cmd.json()))
    
    def _get_response(self, request_id):
        r = self.redis_client.brpop(request_id)
        return json.loads(r[1], encoding="utf8")
    
    def register_service(self, service):
        if not isinstance(service, LakaService):
            raise
        cmd = FofoCommand.New(COMMAND_REGISTER_SERVICE, service.json())
        self._send_command(cmd)
        service = self._get_response(cmd.request_id)
        self.service_id = service["id"]
        return service
    
    def get_service(self, service_id):
        cmd = FofoCommand.New(COMMAND_GET_SERVICE, {"service_id": service_id})
        self._send_command(cmd)
        return self._get_response(cmd.request_id)
    
    def search_service(self, name="", group=""):
        cmd = FofoCommand.New(COMMAND_SEARCH_SERVICE, {"name":name, "group":group})
        self._send_command(cmd)
        return self._get_response(cmd.request_id)

    def health_check(self):
        t = threading.Thread(target=health_check_handler, args=(self, ))
        t.start()
        self.heart_beat_thread = t

    def heart_beat_response(self):
        cmd = FofoCommand.New(COMMAND_HEALTH_CHECK_RESPONSE, {"service_id": self.service_id, "healthCheckTime": int(time.time())})
        self._send_command(cmd)


def health_check_handler(fofo):
    pubsub = fofo.redis_client.pubsub()
    pubsub.subscribe(FOFO_HEALTHCHECK_CHANNEL)
    for msg in pubsub.listen():
        if msg["type"] == "subscribe":
            continue
        fofo.heart_beat_response()