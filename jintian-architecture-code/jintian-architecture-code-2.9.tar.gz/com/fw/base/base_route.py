import cgi
import traceback
from concurrent.futures.thread import ThreadPoolExecutor
from enum import Enum
import falcon
import os
from com.fw.base.base_log import logger
from com.fw.utils.json_serializer import JsonSerializerutils
from com.fw.base.base_exception import BaseException


class Status(Enum):
    OK = '正常',
    ERROR = '异常'


class Result(object):
    def __init__(self, data, status: Status = Status.OK, msg: str = "操作成功"):
        self.status = status.name
        self.msg = msg
        self.data = data

    def __str__(self):
        return str(self.__dict__)


def route_result(func):
    def get_result(self, req, resp):

        try:
            data = Result(func(self, req.params), Status.OK)
        except BaseException as e:
            data = Result("", Status.ERROR, e.err_msg)
        except Exception as ex:

            logger.error("OTHER EXCEPTION:{} ".format(traceback.format_exc()))
            data = Result("", Status.ERROR, "OTHER EXCEPTION :")

        resp.status = falcon.HTTP_200
        resp.body = (JsonSerializerutils.dump_to_json(data))

    return get_result


def route_file_result(func):
    def get_result(self, req, resp):
        params = req.params

        env = req.env
        env.setdefault('QUERY_STRING', '')
        form = cgi.FieldStorage(fp=req.stream, environ=env)

        for param in form.list:
            if param.filename:

                data = param.file.read()

                f2 = open(param.filename, "wb+")
                f2.write(data)
                f2.seek(0, os.SEEK_SET)

                param.file.close()
                params[param.name] = f2
            else:
                params[param.name] = param.value

        try:
            data = Result(func(self, params), Status.OK)
        except BaseException as e:
            data = Result("", Status.ERROR, e.err_msg)
        except Exception as ex:

            logger.error("OTHER EXCEPTION:{} ".format(traceback.format_exc()))
            data = Result("", Status.ERROR, "OTHER EXCEPTION")

        resp.status = falcon.HTTP_200
        resp.body = (JsonSerializerutils.dump_to_json(data))

    return get_result
