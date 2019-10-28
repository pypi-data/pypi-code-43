import logging
import inspect
from tornado.web import RequestHandler
from etornado.error_code_manager import HTTP_OK, ErrorCode, error_code_manager


class AggregateHttMethodMeta(type):

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.head = cls.process
        cls.get = cls.process
        cls.post = cls.process
        cls.delete = cls.process
        cls.patch = cls.process
        cls.put = cls.process
        cls.options = cls.process


class BaseHandler(RequestHandler, metaclass=AggregateHttMethodMeta):

    def initialize(self, thread_pool_executor):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.thread_pool_executor = thread_pool_executor
        self.url_args = []

    def write_error(self, status_code, **kwargs):
        error_code = kwargs.get("ec")
        error_info = error_code_manager.format_error_info(error_code, **kwargs)
        self.logger.error(
            "write error for url[%s], method[%s], error_info[%s]",
            self.request.uri, self.request.method, error_info)
        self.write(error_info)
        self.finish()

    async def process(self, *args, **kwargs):
        method = getattr(self, "do_" + self.request.method.lower(), None)
        self.url_args = args
        if method is None:
            self.send_error(HTTP_OK,
                            ec=ErrorCode.UNSUPPORTED_METHOD,
                            method=self.request.method,
                            url=self.request.uri)
            return
        try:
            r = method()
            if inspect.isawaitable(r):
                r = await r
            error_code, result, error_args = self.__parse_result(r)
        except Exception as e:
            self.logger.exception("exception [%s] catched when call [%s]", e, method)
            raise e
        response = error_code_manager.format_error_info(error_code, **error_args)
        if error_code == ErrorCode.NONE:
            response["result"] = result
        self.write(response)
        self.finish()

    def __parse_result(self, r):
        if isinstance(r, tuple):
            if len(r) != 2:
                raise Exception("tuple result [%s]'s length must be 2")
            if r[0] != ErrorCode.NONE:
                if not isinstance(r[1], dict):
                    raise Exception("error info args must be dict")
                return r[0], {}, r[1]
            else:
                return r[0], r[1], {}
        return ErrorCode.NONE, r, {}
