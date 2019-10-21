from enum import Enum

from asyncore_wsgi import AsyncWebSocketHandler

from com.fw.base.base_exception import BaseException
from com.fw.db.redis_db import redis_db
from com.fw.utils.id_util import IDUtils


class SocketType(Enum):
    QUERY_ORDER = "查询订单"


class SimpleEchoHandler(AsyncWebSocketHandler):

    def handleMessage(self):

        try:
            config = eval(self.data)
        except Exception as e:
            self.close()
            return

        if "path" not in config.keys() or config["path"] not in socket_server.route.keys():
            self.close()
            return

        if "key" not in config.keys() or not socket_server.check_key(config["key"]):
            self.close()
            return

        result = socket_server.route[config["path"]](config)

        result = "" if not result else str(result)

        self.sendMessage(result)

    def handleConnected(self):
        socket_server.add_client(self)

    def handleClose(self):
        socket_server.close_client(self)


class SocketServer(object):

    def __init__(self):
        self.keys = set()
        self.clients = set()
        self.route = {}

    def register(self, key, func):
        if not key or not func:
            raise BaseException("NO PATH OR FUNCTION...")
        self.route[key] = func

    def add_client(self, client):
        self.clients.add(client)

    def close_client(self, client):
        self.clients.remove(client)

    def get_keys(self, time=10 * 60):
        key = IDUtils.get_primary_key("SK:", 8)
        redis_db.set(key, "1", ex=time)
        return key

    def check_key(self,key):
        return redis_db.exists(key)


socket_server = SocketServer()
