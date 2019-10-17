import logging
from functools import partial

import django.apps
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.urls import path
from django.views.decorators.http import require_http_methods

from redmin.forms import LoginForm
from redmin.models import RedminModel
from redmin.utils import memorize, import_class
from .user import LoginView

logger = logging.getLogger(__name__)


@memorize
def get_base_view_class(app_name, action):
    try:
        return import_class(f"{app_name}.views.Base{action.capitalize()}View")
    except:
        return import_class(f"redmin.views.Admin{action.capitalize()}View")


def get_view(model, action):
    app_name = model.__module__.split(".")[0]

    view_name = "%s%sView" % (model.__name__, action.capitalize())
    view = None
    try:
        view = import_class(f'{app_name}.views.{view_name}')
    except:
        try:
            view = type("Dynamic%s" % view_name, (get_base_view_class(app_name, action),), dict(
                model=model,
                __module__=f'{app_name}.{__name__}',

            ))
        except Exception as e:
            logger.error(e)

    return view.as_view()


@login_required
@require_http_methods(["GET"])
def token_request(request):
    return HttpResponse(content=get_token(request))


@memorize
def get_models():
    return [model for model in django.apps.apps.get_models() if issubclass(model, RedminModel)]


def get_admin_domain_patterns(admin_prefix):
    urlpatterns = []
    for model in get_models():
        name = model.__name__
        prefix = f'{admin_prefix}/{name}'
        view = partial(get_view, model)
        urlpatterns += [
            path(f'{prefix}/', view("list"), name=f'{name}-list'),
            path(f'{prefix}/export/', view("export"), name=f'{name}-export'),
            path(f'{prefix}/create/', view("create"), name=f'{name}-create'),
            path(f'{prefix}/<int:pk>/', view("update"), name=f'{name}-update'),
            path(f'{prefix}/<int:pk>/delete/', view("delete"), name=f'{name}-delete'),
        ]

    urlpatterns.append(path(f'{admin_prefix}/token/', token_request))
    return urlpatterns


def get_admin_login_path(_route):
    return path(_route, LoginView.as_view(success_url='/'), kwargs={'authentication_form': LoginForm})
