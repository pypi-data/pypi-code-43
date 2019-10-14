#! /usr/bin/python3

"""
基于 redis 队列 的 rpc 框架
"""

import uuid
import json
import redis
import logging

from command import Command
from response import Response



class Laka(object):
    """
    Laka is a json rpc client, based on redis queue.
    """

    def __init__(self, redis_host, redis_port, request_queue, response_message, redis_db=0):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.request_queue = request_queue
        self.redis_client = None
        if not isinstance(response_message, dict):
            raise Exception("Invalid type of response_message, dict is expected but {} found".format(type(response_message)))
        self._connect_redis()
        self.response_message = response_message
    
    # def add_response_message(data):
    #     if not isinstance(data, dict):
    #         raise Exception("Invalid type, dict is expected but {} found".format(type(data)))
    #     self.response_message = data
    
    # def get_message(self, resp_code):
    #     return self.response_message[resp_code]

    def _connect_redis(self):
        self.redis_client = redis.Redis(host=self.redis_host, port=self.redis_port, db=self.redis_db)

    def send(self, code, data):
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
            logging.error(e)
            return None
        return data
    
    def accept_request(self):
        while True:
            data = self._accept(self.request_queue)
            if not data:
                continue
            try:
                cmd = Command.load_from_dict(data)
            except Exception as e:
                logging.error(e)
                continue
            yield cmd
        
    def accept_response(self, request_id):
        data = self._accept(request_id)
        try:
            response = Response.load_from_dict(data)
        except Exception as e:
            logging.error(e)
            return None
        message = self.response_message.get(response.code) if response.code != 0 else ""
        response.set_message(message)
        return response

    
    def response(self, request_id, code, data):
        """
        由于发送返回数据时，需要知道 request_id，因此如果请求时数据格式不正确或者缺少 request_id，则该请求将得不到任何返回值。
        所以必须确保发送请求时数据格式正确。
        """
        message = self.response_message.get(code) if code != 0 else ""
        resp = Response(request_id, code, data)
        resp.set_message(message)
        data = json.dumps(resp.json())
        self.redis_client.lpush(request_id, data)

    def error_response(self, request_id, code):
        self._response(request_id, code, None)
    
    def success_response(self, request_id, data):
        self._response(request_id, 0, data)
    
    # def response(self, resp):
    #     if not isinstance(resp, Response):
    #         raise Exception("Invalid response, type Response is expected, but {} found".format(type(resp)))
    #     if resp.code == 0:
    #         self.success_response(resp.request_id, resp.data)
    #     else:
    #         self.error_response(resp.request_id, resp.code)


    def new_request_id(self):
        return "KAKA:REQUEST_ID:"+uuid.uuid4().hex