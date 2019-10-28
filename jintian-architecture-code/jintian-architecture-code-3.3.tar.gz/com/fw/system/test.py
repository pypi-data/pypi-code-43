import os

import tornado
from tornado.options import define, options
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

from com.fw.base.base_exception import BaseException
from com.fw.db.redis_db import redis_db
from com.fw.system.red_conf import system_conf
from com.fw.utils.id_util import IDUtils


class SocketServer():

    def __init__(self):
        self.checkKey = False
        self.client = {}
        self.route = {}
        self.keys = set()

        # 设置服务器端口
        define("port", default=8001, type=int)

        if system_conf.has_group("socket"):
            self.checkKey = system_conf.get_value("socket","checkKey")

    def send_message(self,key, message):
        '''
        发送消息
        :param key:
        :param message:消息内容
        :return:
        '''
        if key not in self.client.keys():
            raise BaseException("客户端断开连接...")
        self.client[key].write_message(message)

    def run(self):

        tornado.options.parse_command_line()

        app = tornado.web.Application([
            (r"/websocket", ChatHandler)
        ],
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            template_path=os.path.join(os.path.dirname(__file__), "template"),
            debug=True
        )

        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.current().start()

    def register(self, key, func = None):
        if not key :
            raise BaseException("NO PATH ...")
        self.route[key] = func

    def get_keys(self,key = None, time=15 * 60):
        if not key:
            key = IDUtils.get_primary_key("SK:", 8)
        redis_db.set(key, "1", ex=time)
        return key

    def check_key(self, key):
        return redis_db.exists(key)

    def rm_key(self,key):
        redis_db.delete(key)

    def close(self,key):
        if key in self.client.keys():
            self.client[key].close()


class ChatHandler(WebSocketHandler):

    def open(self):
        param = self.request.query_arguments

        if "path" not in param.keys() or "key" not in param.keys():
            self.close()

        self.path = param["path"]
        self.key = param["key"]

        '''
        地址不存在
        '''
        if self.path not in socket.route.keys():
            self.write_message("ILLEGAL INVOCATION...")
            self.close()
            return

        if self.checkKey == "True" and self.key in socket.client.keys():
            self.write_message("Repeated client...")
            self.close()
            return

        # Register.
        socket.client[self.key] = self
        socket.get_keys(self.key, 15 * 60)

    def on_message(self, message):
        if message == "heart":
            self.write_message("heart")
        else:
            result = socket.route[self.path](message)
            if not result or result == "":
                result = "heart"

            self.write_message(result)

    def on_close(self):
        # Unregister.
        socket.client.pop(self.key)
        socket.rm_key(self.key)

    def check_origin(self, origin):
        return True  # 允许WebSocket的跨域请求



socket = SocketServer()




def test():
    print("------")
