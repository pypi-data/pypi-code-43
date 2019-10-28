import tornado.ioloop
import tornado.web
import tornado.httpserver
import logging.config
from concurrent.futures import ThreadPoolExecutor
from etornado.buildin_handlers.unsupported_url_handler import UnsupportedUrlHandler


class Application(object):
    def __init__(self, port, process_count=0, thread_pool_size=0, logging_config=None):
        if logging_config is not None:
            logging.config.fileConfig(logging_config)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.stopping = False
        self.handlers = []
        self.port = port
        self.process_count = process_count
        self.thread_pool_executor = None
        if thread_pool_size > 0:
            self.thread_pool_executor = ThreadPoolExecutor(
                    max_workers=thread_pool_size)

    def register_handler(self, url, klass):
        self.handlers.append((url, klass))

    def stop(self):
        self.logger.info("call stop")
        self.stopping = True

    def run(self):
        self.logger.info("start service ...")
        handlers = self.get_handlers()
        self.logger.info("register %d handlers[%s]", len(handlers), handlers)
        app = tornado.web.Application(handlers)
        server = tornado.httpserver.HTTPServer(app)
        server.bind(self.port)
        server.start(self.process_count)
        tornado.ioloop.PeriodicCallback(self.check_stop, 100).start()
        tornado.ioloop.IOLoop.current().start()

    def get_handlers(self):
        result = []
        handler_args = dict(thread_pool_executor=self.thread_pool_executor)
        for url, handler in self.handlers:
            result.append((url, handler, handler_args))
        result.append((r".*", UnsupportedUrlHandler, handler_args))
        return result

    def check_stop(self):
        if self.stopping:
            self.logger.info("stop service ...")
            if self.thread_pool_executor:
                self.thread_pool_executor.shutdown(False)
            tornado.ioloop.IOLoop.current().stop()
            self.logger.info("stop service success!!!")
