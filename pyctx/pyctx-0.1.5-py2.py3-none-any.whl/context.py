import json
import os
import threading
import uuid
import logging
from logging import Logger
from typing import Dict, Any, Tuple
from datetime import datetime
from contextlib import contextmanager

from .context_data import ContextData

req_logger: Logger = logging.getLogger("REQ")


class Context:
    __TIMESTAMP_FORMAT__ = "%Y-%m-%d %H:%M:%S.%f"

    def __init__(self, ctx_type):
        context_id = str(uuid.uuid4())
        self.ctx_type = ctx_type
        self.context_id = context_id
        self.start_time = datetime.now()
        self.end_time = None
        self.pid = os.getpid()
        self.thread_name = threading.current_thread().getName()
        self._data = {}
        self.log = ContextLog(self)
        self.log.start_timer('ALL')

    # @property
    # def logger(self):
    #     return get_application_logger(context_id=self.context_id)

    def get(self, key, default=None, set_if_missing=False):
        if set_if_missing:
            return self._data.setdefault(key, default)
        else:
            return self._data.get(key, default)

    def remove(self, key):
        del self._data[key]

    @staticmethod
    def now() -> datetime:
        """Return current time as datetime object"""
        return datetime.now()

    def finalize(self) -> dict:
        if self.end_time is None:
            self.end_time = Context.now()
        self.log.stop_timer('ALL')
        data, timers = self.log.finalize()

        return {
            'type': self.ctx_type,
            'ctxId': self.context_id,
            'startTime': self.start_time.strftime(self.__TIMESTAMP_FORMAT__),
            'endTime': self.end_time.strftime(self.__TIMESTAMP_FORMAT__),
            'data': data,
            'timers': timers,
        }


class RequestContext(Context):
    def __init__(self, request):
        super(RequestContext, self).__init__('REQ')
        now = Context.now()
        req_id = str(uuid.uuid4())

        # fill required values
        self.request = request
        self.request_id = req_id
        self.log.start_timer('request', now)
        self.start_time, self.end_time = now, None
        # self.logger = self.__get_application_logger(request_id=req_id)

        self.response = None
        self.http_data = None
        self.view_name = None

    def set_response(self, response):
        self.response = response

    def set_http_data(self, data):
        self.http_data = data

    def set_view_name(self, view):
        self.view_name = view

    def finalize(self) -> dict:
        now = RequestContext.now()
        self.end_time = now
        self.log.stop_timer('request', now)

        self.http_data.update({'view': self.view_name})

        dict_to_log: dict = {
            **super().finalize(),
            'reqId': self.request_id,
            'http': self.http_data,
        }

        log = None
        try:
            log = json.dumps(dict_to_log)
        except Exception as e:
            print(f'Error occurred while serializing the context data. Error: {e}' + str(dict_to_log))
        finally:
            if log is None:
                log = str(dict_to_log)  # NOTE: Watch error case for improvements.
                # This print data with single quotes (not valid json)
            req_logger.info(log)

        return dict_to_log


class ContextLog:
    def __init__(self, ctx: Context):
        self._ctx = ctx
        self._data = ContextData()
        self._timers = ContextData()

    def get_data(self, key: str, default=None) -> Any:
        return self._data.get(key, default=default)

    def set_data(self, key: str, value) -> 'ContextLog':
        self._data.update({key: value})
        return self

    def add_data(self, key, value) -> 'ContextLog':
        """Add the given value to given key"""
        if key not in self._data:
            self.set_data(key, value)
        else:
            if isinstance(self._data[key], list):
                self._data[key].append(value)
            else:
                self._data[key] = [self._data[key], value]
        return self

    def set_status(self, key, value) -> 'ContextLog':
        """
        Set binary value for the given value to key
        If value is truthy value then value of the key is True
        Else, value of the key is False
        """
        return self.set_data(key, True if value else False)

    def get_status(self, key) -> bool:
        return True if self.get_data(key) else False

    def start_timer(self, timer_name: str, current_time: datetime = None) -> 'ContextLog':
        now = current_time if current_time is not None else Context.now()
        self._timers[timer_name] = now
        return self

    def stop_timer(self, timer_name: str, current_time: datetime = None) -> 'ContextLog':
        """Calculate timedelta and return its to milliseconds"""
        now = current_time if current_time is not None else Context.now()
        self._timers[timer_name] = now - self._timers[timer_name]
        return self

    @contextmanager
    def timeit(self, timer_name):
        """This is a context manager to calculate execution time for a code block.

        Examples:
            with ctx_instance.timeit('timer1'):
               # code block
        """
        try:
            self.start_timer(timer_name)
            yield
        finally:
            self.stop_timer(timer_name)

    def finalize(self) -> Tuple[ContextData, Dict]:
        data = self._data.flat()
        timers = ContextData(**{k: v.total_seconds() for k, v in self._timers.items()}).flat()
        return data, timers
