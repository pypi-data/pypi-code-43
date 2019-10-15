import inspect

from apistar import App
from apistellar.helper import _build_new_func
from apistellar import route, settings, Session, redirect

__version__ = "0.0.2"


def init(url_prefix="/cas", name="cas"):
    from .routing import CasController
    settings._json.setdefault('CAS_TOKEN_SESSION_KEY', '_CAS_TOKEN')
    settings._json.setdefault('CAS_USERNAME_SESSION_KEY', 'CAS_USERNAME')
    settings._json.setdefault('CAS_ATTRIBUTES_SESSION_KEY', 'CAS_ATTRIBUTES')
    settings._json.setdefault('CAS_LOGIN_ROUTE', '/cas')
    settings._json.setdefault('CAS_LOGOUT_ROUTE', '/cas/logout')
    settings._json.setdefault('CAS_VALIDATE_ROUTE', '/cas/serviceValidate')
    # Requires CAS 2.0
    settings._json.setdefault('CAS_AFTER_LOGOUT', None)
    route(url_prefix, name)(CasController)


def login_required():

    def auth(func):
        args = inspect.getfullargspec(func).args
        args_def = ", ".join(args)
        func_def = """
@wraps(func)
async def wrapper(__container, __app, {}):
    from collections.abc import Awaitable
    if username not in __container:
        return redirect(app.reverse_url("view:cas:login"))
    awaitable = func({})
    if isinstance(awaitable, Awaitable):
        return await awaitable
    return awaitable
        """.format(args_def, args_def)
        return _build_new_func(
            func_def, func,
            {"redirect": redirect,
             "username": settings.CAS_USERNAME_SESSION_KEY},
            {"__container": Session, "__app": App})

    return auth
