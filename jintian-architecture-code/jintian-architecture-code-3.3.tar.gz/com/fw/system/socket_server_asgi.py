import asyncio
import os

import tornado
from tornado.options import define, options
from tornado.web import RequestHandler, StaticFileHandler
from tornado.websocket import WebSocketHandler

from com.fw.base.base_exception import BaseException
from com.fw.base.base_log import logger
from com.fw.db.redis_db import redis_db
from com.fw.utils.id_util import IDUtils


class SocketServer():

    def __init__(self):
        self.checkKey = False
        self.client = {}
        self.route = {}
        self.keys = set()

        # 设置服务器端口
        define("port", default=8001, type=int)

    def send_message(self, key, message):
        '''
        发送消息
        :param key:
        :param message:消息内容
        :return:
        '''
        if key not in self.client.keys():
            raise BaseException("客户端断开连接...")
        self.client[key].write_message(message)

    def run(self, work_dir):

        tornado.options.parse_command_line()

        asyncio.set_event_loop(asyncio.new_event_loop())

        app = tornado.web.Application([
            (r"/websocket", ChatHandler), (r'/apidoc/(.*)', StaticFileHandler,
                                           dict(path=os.path.join(work_dir, 'static/apidoc'),
                                                default_filename='index.html')),
            (r'/test/(.*)', StaticFileHandler,
             dict(path=os.path.join(work_dir, 'static/test'),
                  default_filename='index.html'))
        ],
            debug=True
        )

        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(options.port)
        logger.info("--------- socket 启动成功 --------")
        tornado.ioloop.IOLoop.current().start()

    def register(self, key, func=None, check_key=True):
        if not key:
            raise BaseException("NO PATH ...")
        self.route[key] = {"func": func, "check_key": check_key}

    def get_keys(self, key=None, time=15 * 60):
        if not key:
            key = IDUtils.get_primary_key("SK:", 8)
        redis_db.set(key, "1", ex=time)
        return key

    def check_key(self, key):
        return redis_db.exists(key)

    def rm_key(self, key):
        redis_db.delete(key)

    def close(self, key):
        if key in self.client.keys():
            self.client[key].close()


class MyFile(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")


class ChatHandler(WebSocketHandler):

    def open(self):
        param = self.request.query_arguments

        if "path" not in param.keys() or "key" not in param.keys():
            self.close()
            return

        self.path = str(param["path"][0], encoding="utf-8")
        self.key = str(param["key"][0], encoding="utf-8")

        '''
        地址不存在
        '''
        if self.path not in socket.route.keys():
            self.write_message("ILLEGAL INVOCATION...")
            self.close()
            return

        self.check_key = socket.route[self.path]["check_key"]
        self.func = socket.route[self.path]["func"]

        if self.check_key == True:
            if self.key in socket.client.keys():
                self.write_message("Repeated client...")
                self.close()
                return
            socket.get_keys(self.key, 15 * 60)

        # Register.
        socket.client[self.key] = self
        self.write_message("ok")

    def on_message(self, message):

        if self.check_key and not socket.check_key(self.key):
            self.write_message("Time out...")
            self.close()
            return

        if message == "heart" or not self.func:
            self.write_message("heart")
        else:
            try:
                result = self.func(message)
            except BaseException as e:
                self.write_message(e.err_msg)
                self.close()
            except Exception as e:
                result = "ERROR:请联系管理员..."

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

