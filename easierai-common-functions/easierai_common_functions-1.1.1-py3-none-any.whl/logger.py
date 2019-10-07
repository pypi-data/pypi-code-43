import logging
from logging.handlers import TimedRotatingFileHandler
import datetime as dt
import time
import inspect
import os
import sys
from copy import copy

import json

import common_functions.constants as constants

class ConsoleFormatter(logging.Formatter):
    
    def __init__(self):
        fmt = '%(asctime)s [%(levelname)-7s - %(filename)s] %(message)s %(add_info)s'
        datefmt = '%Y-%m-%d %H:%M:%S'
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, record):
        record_copy = copy(record)
        j = json.loads(record.msg)
        record_copy.msg = j['message']
        record_copy.filename = j['source_file']
        if 'additional_info' in j:
            record_copy.add_info = '-> '+j['additional_info']
        else:
            record_copy.add_info = ''
        return super().format(record_copy)

class Logger:

    def __init__(self, base_folder, service, source_file):
        self.service = service
        self.source_file = source_file
        self.base_folder = base_folder
        self.init_log_file()

    def lineno(self):
        f = inspect.currentframe()
        filename = os.path.normcase(f.f_code.co_filename)
        # Traverse the stack until the function has been called by a different file, then get that line number
        while filename == __file__:
            f = f.f_back
            filename = os.path.normcase(f.f_code.co_filename)

        return f.f_lineno

    def init_log_file(self):
        streamHandler = logging.StreamHandler(sys.stdout)
        streamHandler.setFormatter(ConsoleFormatter())
        self.logger_info = logging.getLogger(self.service + '-info')
        self.logger_info.setLevel(logging.INFO)
        self.logger_debug = logging.getLogger(self.service + '-debug')
        self.logger_debug.setLevel(logging.DEBUG)
        self.logger_warning = logging.getLogger(self.service + '-warning')
        self.logger_warning.setLevel(logging.WARNING)
        self.logger_error = logging.getLogger(self.service + '-error')
        self.logger_error.setLevel(logging.ERROR)
        self.logger_perf = logging.getLogger(self.service + '-performance')
        self.logger_perf.setLevel(logging.INFO)
        if not self.logger_info.handlers:
            handler_info = TimedRotatingFileHandler(self.base_folder + self.service + '-INFO.log', when='d', interval=1, backupCount=4)
            self.logger_info.addHandler(streamHandler)
            self.logger_info.addHandler(handler_info)
            handler_debug = TimedRotatingFileHandler(self.base_folder + self.service + '-DEBUG.log', when='d', interval=1, backupCount=4)
            self.logger_debug.addHandler(streamHandler)
            self.logger_debug.addHandler(handler_debug)
            handler_warning = TimedRotatingFileHandler(self.base_folder + self.service + '-WARNING.log', when='d', interval=1, backupCount=4)
            self.logger_warning.addHandler(streamHandler)
            self.logger_warning.addHandler(handler_warning)
            handler_error = TimedRotatingFileHandler(self.base_folder + self.service + '-ERROR.log', when='d', interval=1, backupCount=4)
            self.logger_error.addHandler(streamHandler)
            self.logger_error.addHandler(handler_error)
            handler_perf = TimedRotatingFileHandler(self.base_folder + self.service + '-PERFORMANCE.log', when='d', interval=1, backupCount=4)
            self.logger_perf.addHandler(streamHandler)
            self.logger_perf.addHandler(handler_perf)


    def generate_log_doc(self, level, message, additional_info=None):
        doc = {
            'service': self.service,
            'source_file': self.source_file + ':' + str(self.lineno()),
            '@timestamp': dt.datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        if additional_info:
            doc['additional_info'] = additional_info
        return json.dumps(doc)

    def debug(self, message, additional_info=None):
        self.logger_debug.debug(self.generate_log_doc(constants.DEBUG, message, additional_info))

    def info(self, message, additional_info=None):
        self.logger_info.info(self.generate_log_doc(constants.INFO, message, additional_info))

    def warning(self, message, additional_info=None):
        self.logger_warning.warning(self.generate_log_doc(constants.WARNING, message, additional_info))

    def error(self, message, additional_info=None):
        self.logger_error.error(self.generate_log_doc(constants.ERROR, message, additional_info))

    def perf(self, message, additional_info=None):
        self.logger_perf.info(self.generate_log_doc(constants.PERFORMANCE, message, additional_info))
