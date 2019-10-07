import functools
from events import Events

from ...share.utils import safe_func


class RoutesMixin(object):
    """
    专门做路由管理
    """

    rule_map = None

    def __init__(self):
        self.rule_map = dict()

    def add_route_rule(self, cmd, view_func, endpoint=None):
        if cmd in self.rule_map and view_func != self.rule_map[cmd]['view_func']:
            raise Exception(
                'duplicate view_func for cmd: %(cmd)s, old_view_func: %(old_view_func)s, new_view_func: %(new_view_func)s' % dict(
                    cmd=cmd,
                    old_view_func=self.rule_map[cmd]['view_func'],
                    new_view_func=view_func,
                )
            )

        self.rule_map[cmd] = dict(
            endpoint=endpoint or view_func.__name__,
            view_func=view_func,
        )

    def route(self, cmd, endpoint=None):
        def decorator(func):
            self.add_route_rule(cmd, func, endpoint)
            return func
        return decorator

    def get_route_rule(self, cmd):
        return self.rule_map.get(cmd)


def _reg_event_handler(func):
    @functools.wraps(func)
    def func_wrapper(obj, handler):
        event = getattr(obj.events, func.__name__)
        event += safe_func(handler)

        return handler
    return func_wrapper


class Router(RoutesMixin):
    """
    不支持blueprint的原因是为了性能考虑
    """
    events = None

    def __init__(self):
        RoutesMixin.__init__(self)
        self.events = Events()

    @_reg_event_handler
    def start_worker(self, f):
        """
        start
        f(app)
        """

    @_reg_event_handler
    def stop_worker(self, f):
        """
        stop
        f(app)
        """

    @_reg_event_handler
    def before_update(self, f):
        """
        update之前
        f(app, dt_ms)
        """

    @_reg_event_handler
    def after_update(self, f):
        """
        update之后
        f(app, dt_ms)
        """

    @_reg_event_handler
    def before_request(self, f):
        """
        request之前
        f(request)
        """

    @_reg_event_handler
    def after_request(self, f):
        """
        request之后
        f(request, exc)
        """

    @_reg_event_handler
    def before_response(self, f):
        """
        response之前
        f(request, response)
        """

    @_reg_event_handler
    def after_response(self, f):
        """
        response之后
        f(request, response)
        """

    @_reg_event_handler
    def close_client(self, f):
        """
        client close之后.
        f(request)
        """
