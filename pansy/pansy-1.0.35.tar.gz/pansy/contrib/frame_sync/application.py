from ... import BaseListener, constants
from ...share.log import logger
from ...share.utils import safe_call
from .request import Request


class Application(BaseListener):

    box_class = None
    router = None

    def on_start(self):
        assert self.router is not None

        self.router.events.start_worker(self)

    def on_stop(self):
        self.router.events.stop_worker(self)

    def on_update(self, dt, task_list):
        dt_ms = round(dt * 1000)

        self.router.events.before_update(self, dt_ms)

        # logger.debug('dt_ms: %s, task_list: %s', dt_ms, task_list)
        if task_list:
            logger.debug('dt_ms: %s, task_list: %s', dt_ms, task_list)

            for task in task_list:
                safe_call(self._handle_task, task)

        self.router.events.after_update(self, dt_ms)

    def write_to_users(self, *args, **kwargs):
        """
        格式为
        [(uids, box), (uids, box), (uids, box) ...]
        :param data_list:
        :return:
        """
        func_name = 'write_to_users'

        self.router.events.before_response(self, (func_name, args, kwargs))
        try:
            return self.worker.write_to_users(*args, **kwargs)
        finally:
            self.router.events.after_response(self, (func_name, args, kwargs))

    def close_users(self, *args, **kwargs):
        func_name = 'close_users'

        self.router.events.before_response(self, (func_name, args, kwargs))
        try:
            return self.worker.close_users(*args, **kwargs)
        finally:
            self.router.events.after_response(self, (func_name, args, kwargs))

    def _handle_task(self, task):
        request = Request(self, task)

        if not request.is_valid:
            logger.error('invalid request. request: %s' % request)
            return

        if task.cmd == constants.CMD_CLIENT_CLOSED:
            self.router.events.close_client(request)
            return

        if not request.view_func:
            logger.error('cmd invalid. request: %s' % request)
            return False

        self.router.events.before_request(request)
        view_func_exc = None

        try:
            request.view_func(request)
        except Exception as e:
            logger.error('view_func raise exception. request: %s, e: %s',
                         request, e, exc_info=True)
            view_func_exc = e

        self.router.events.after_request(request, view_func_exc)
