'''
Provides interface to setup the web server using aiohttp web.run_app
'''
import asyncio
from enum import Enum
from typing import Dict, Callable

from aiohttp import web

from arps.apps.pid import create_pid_file


class HTTPMethods(Enum):
    GET, POST, PUT, DELETE = range(4)


class RoutesBuilder():
    def __init__(self):
        self._routes = {method: {} for method in HTTPMethods}

    def add_get(self, get_routes):
        self._routes[HTTPMethods.GET].update(get_routes)
        return self

    def add_post(self, post_routes):
        self._routes[HTTPMethods.POST].update(post_routes)
        return self

    def add_put(self, put_routes):
        self._routes[HTTPMethods.PUT].update(put_routes)
        return self

    def add_delete(self, delete_routes):
        self._routes[HTTPMethods.DELETE].update(delete_routes)
        return self

    @property
    def routes(self):
        return self._routes

def run_server(port: int, routes: Dict[HTTPMethods, Dict[str,Callable]], *, static_routes=None, cleanup=None):
    '''
    Args:
    - port: Port to listen
    - routes: a dict containing the routes (pair of URL and function mapped) related to a HTTP Method
    - static_routes: a dict containing the static route and the tuple mapped to this route (path, resource name)
    - cleanup: function to be called when the server termitates
    '''

    try:
        static_routes = static_routes or dict()
        app = setup_server(routes, static_routes)
        if cleanup:
            app.on_cleanup.append(cleanup)
        with create_pid_file():
            web.run_app(app, port=port)
    except OSError as err:
        raise RuntimeError(f'Unable to start the service: {err}')

def setup_server(routes, static_routes, debug=False):
    '''
    Setup server, debug toolbar, and routes

    Returns app to be ran
    '''

    #https://stackoverflow.com/questions/24774980/why-cant-i-catch-sigint-when-asyncio-event-loop-is-running/24775107#24775107
    loop = asyncio.get_event_loop()

    def wakeup():
        # Call again
        loop.call_later(0.5, wakeup)

    loop.call_later(0.5, wakeup)

    if debug:
        from aiohttp_debugtoolbar import toolbar_middleware_factory
        import aiohttp_debugtoolbar
        app = web.Application(middlewares=[toolbar_middleware_factory,
                                           web.normalize_path_middleware(append_slash=True, merge_slashes=True)],
                              debug=True)
        aiohttp_debugtoolbar.setup(app)
    else:
        app = web.Application(middlewares=[web.normalize_path_middleware(append_slash=True, merge_slashes=True)])

    setup_route(routes, static_routes, app)

    return app


def setup_route(routes, static_routes, app):
    for method in HTTPMethods:
        for route, function in routes[method].items():
            app.router.add_route(method.name, route, function)

    for route, function in static_routes.items():
        app.router.add_static(route, path=function[0], name=function[1])
