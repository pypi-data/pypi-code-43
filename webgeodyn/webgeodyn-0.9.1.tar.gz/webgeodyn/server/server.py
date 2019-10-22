import tornado.ioloop as ioloop
import tornado.web as web
from tornado.httpserver import HTTPServer
from tornado.log import enable_pretty_logging, gen_log
from tornado.concurrent import run_on_executor

import json
import signal
import os
import sys
import urllib
import webbrowser
import uuid
import logging

from webgeodyn.server.datahandlers import *
from webgeodyn.obsdata import ObsData

static_path = os.path.normpath(os.path.join(os.path.dirname(__file__) , "..", "www"))  # path of static files
listeningport = 8080


class CloseHandler(RequestHandler):
    closeUUID = str(uuid.uuid4())

    def get(self):
        self.write(json.dumps({'closeUUID': self.closeUUID}))

    def post(self):
        gen_log.info("User closed web browser.")
        str_data = tornado.escape.url_unescape(self.request.body)
        json_request = json.loads(str_data)
        if json_request.get("closeUUID") == self.closeUUID:
            ioloop.IOLoop.current().add_timeout(datetime.timedelta(seconds=1), stopServer)


def stopServer(*args):
    gen_log.info(" Asking server to exit...")
    ioloop.IOLoop.current().stop()


def startServer(models, allowclose=True, showbrowser=True, debug=False):
    import tornado.options

    obsdata = ObsData()

    DEFAULT_LEVEL = logging.DEBUG
    DEFAULT_FORMAT = '[%(levelname)s - %(asctime)s] %(message)s'

    # Enable logging through tornado.web.Application.log_request in stdout
    tornado.log.enable_pretty_logging()

    # Logging in seperate files (not used for now)
    # access_file = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'log/access.log'))
    # access_file.setLevel(DEFAULT_LEVEL)
    # access_file.setFormatter(tornado.log.LogFormatter(fmt=DEFAULT_FORMAT))
    # tornado.log.access_log.addHandler(access_file)
    # general_file = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'log/general.log'))
    # general_file.setLevel(DEFAULT_LEVEL)
    # general_file.setFormatter(tornado.log.LogFormatter(fmt=DEFAULT_FORMAT))
    # tornado.log.gen_log.addHandler(general_file)
    # app_file = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'log/app.log'))
    # tornado.log.app_log.addHandler(app_file)

    # Custom log function to have more info than the default logging function
    def log_function(handler):
        if handler.get_status() < 400:
            log_method = access_log.info
        elif handler.get_status() < 500:
            log_method = access_log.warning
        else:
            log_method = access_log.error
        request_time = 1000.0 * handler.request.request_time()
        request_ip = handler.request.headers.get('X-Real-IP') or handler.request.remote_ip

        log_method("{0} {1.method} {1.uri} ({1.host} {2}) in {3:.2f}ms"
                   .format(handler.get_status(), handler.request, request_ip, request_time))
        return

    settings = {
        "cookie_secret": str(uuid.uuid4()),
        "autoreload": debug,
        "debug": debug,
        "log_function": log_function,
        #"login_url": "/"
    }

    handlers = [
        url(r"/getdatalist", DataListHandler, {"models": models, "obsdata": obsdata}),
        url(r"/getglobedata", GlobeDataHandler, {"models": models, "obsdata": obsdata}),
        url(r"/getloddata", LodDataHandler, {"models": models, "obsdata": obsdata}),
        url(r"/getspherharmdata", SpherHarmDataHandler, {"models": models, "obsdata": obsdata}),
        url(r"/getspectradata", SpectraDataHandler, {"models": models, "obsdata": obsdata}),
        url(r"/gettimeseriedata", TimeSerieDataHandler, {"models": models, "obsdata": obsdata}),
        url(r"/getobservatorydata", ObservatoryDataHandler, {"models": models, "obsdata": obsdata}),
        url(r"/getexportfileinfo", ExportFileInfoHandler, {"models": models, "obsdata": obsdata}),
    ]

    if allowclose:
        handlers.append(url(r"/close", CloseHandler))

    # Add file handler for each model that link to the directory of the zip archive for export
    for model_name, model in models.items():
        handlers.append(url(r'/'+model_name+r'/('+model_name+r'\.zip)', StaticFileHandler, {'path': model.dataDirectory}))

    handlers.append(url(r'/(.*)', StaticFileHandler,
        {'path': static_path, 'default_filename': 'index.html'}))

    app = tornado.web.Application(handlers, **settings)

    server = app.listen(listeningport, xheaders=True)

    loop = ioloop.IOLoop.current()
    #signal.signal(signal.SIGQUIT, sig_exit) # SIGQUIT is send by our supervisord to stop this server.
    #signal.signal(signal.SIGTERM, sig_exit) # SIGTERM is send by Ctrl+C or supervisord's default.
    #signal.signal(signal.SIGINT, sig_exit)

    gen_log.info('Server listening to ' + str(listeningport))

    if showbrowser:
        webbrowser.open("http://localhost:"+str(listeningport)+"/", new=1, autoraise=True)

    try:
        loop.start()
    except KeyboardInterrupt:
        gen_log.info("KeyboardInterrupt")
        stopServer()

    server.stop()
    gen_log.info("Server stopped.")
