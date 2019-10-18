# -*- coding: utf-8 -*-
"""CAS login/logout replacement views"""
import json
import uuid
import traceback
import logging

import requests
from six.moves.urllib_parse import urlencode
from six.moves import urllib_parse as urlparse
from operator import itemgetter
from django.core.files.storage import default_storage, FileSystemStorage
from django.contrib import auth
from django.http import (
    HttpResponseRedirect,
    HttpResponseForbidden,
    HttpResponse,
    HttpResponseNotAllowed,
)
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils import translation
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from .utils import _redirect_url, _get_session, _logout_url, is_authenticated

from cas.domain import Domain


__all__ = ["login", "logout"]
logger = logging.getLogger("default")


def is_secure(request):
    return getattr(settings, "IS_SECURE", request.is_secure())


def _service_url(request, redirect_to=None, gateway=False, path=None):
    """Generates application service URL for CAS"""
    protocol = "https://"
    host = request.domain.host
    if not path:
        path = request.path
    service = protocol + host + path
    if redirect_to:
        if "?" in service:
            service += "&"
        else:
            service += "?"
        if gateway:
            """ If gateway, capture params and reencode them before returning a url """
            gateway_params = [(REDIRECT_FIELD_NAME, redirect_to), ("gatewayed", "true")]
            query_dict = request.GET.copy()
            try:
                del query_dict["ticket"]
            except Exception:
                pass
            query_list = query_dict.items()

            # remove duplicate params
            for item in query_list:
                for index, item2 in enumerate(gateway_params):
                    if item[0] == item2[0]:
                        gateway_params.pop(index)
            extra_params = gateway_params + query_list

            # Sort params by key name so they are always in the same order.
            sorted_params = sorted(extra_params, key=itemgetter(0))
            service += urlencode(sorted_params)
        else:
            service += urlencode({REDIRECT_FIELD_NAME: redirect_to})
    return service


def _login_url(service, ticket="ST", gateway=False, cas_url=""):
    """Generates CAS login URL"""
    LOGINS = {"ST": "login", "PT": "proxyValidate"}
    if gateway:
        params = {"service": service, "gateway": True}
    else:
        params = {"service": service}
    if not ticket:
        ticket = "ST"
    login = LOGINS.get(ticket[:2], "login")

    return urlparse.urljoin(cas_url, login) + "?" + urlencode(params)


def login_url(request, next_page="/", path=None):
    ticket = request.GET.get("ticket")
    cas_url = request.domain.auth.url + "/cas/"
    service = _service_url(request, next_page, False, path)
    return _login_url(service, ticket, False, cas_url)


def login(request, next_page=None, required=False, gateway=False):
    """Forwards to CAS login URL or verifies CAS ticket"""

    if not next_page:
        next_page = _redirect_url(request)
    if is_authenticated(request.user):
        return HttpResponseRedirect(next_page)
    ticket = request.GET.get("ticket")
    cas_url = request.domain.auth.url + "/cas/"
    service = _service_url(request, next_page, False)

    if ticket:
        user = auth.authenticate(ticket=ticket, service=service, cas_url=cas_url)
        if user is not None:
            # Has ticket, logs in fine
            auth.login(request, user)
            return HttpResponseRedirect(next_page)
        elif settings.CAS_RETRY_LOGIN or required:
            # Has ticket,
            return HttpResponseRedirect(_login_url(service, ticket, False, cas_url))
        else:
            logger.warning(
                "User has a valid ticket but not a valid session, ticket is %s, service is %s, url is %s"
                % (ticket, service, cas_url)
            )
            error = "<h1>Forbidden</h1><p>Login failed.</p>"
            return HttpResponseForbidden(error)
    else:
        if gateway:
            return HttpResponseRedirect(
                _login_url(service, ticket, True, cas_url=cas_url)
            )
        else:
            return HttpResponseRedirect(
                _login_url(service, ticket, False, cas_url=cas_url)
            )


def logout(request, next_page=None):
    """Redirects to CAS logout page"""
    cas_logout_request = request.POST.get("logoutRequest", "")
    if cas_logout_request:
        session = _get_session(cas_logout_request)
        request.session = session
    auth.logout(request)

    if not next_page:
        next_page = _redirect_url(request)

    CAS_LOGOUT_COMPLETELY = getattr(settings, 'CAS_LOGOUT_COMPLETELY', None)
    if CAS_LOGOUT_COMPLETELY:
        return HttpResponseRedirect(_logout_url(request, next_page))
    else:
        return HttpResponseRedirect(next_page)


@api_view(["PUT"])
def language(request: Request) -> Response:
    """language 设置语言
    """
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    pk = request.user.hacId
    url = f"{request.domain.hac.url}/api/admin/users/{pk}/language"
    response = requests.put(
        url,
        json={"data": {"language": request.data.get("language", "zh_CN")}},
        headers={"identify": request.domain.hac.identify},
        timeout=10,
    )
    if response.status_code == 200 and response.json().get("code", None) == "200000":
        return Response(
            {"message": "操作成功"}, content_type="application/json;charset = utf-8"
        )
    return Response(
        {"message": "操作失败"},
        content_type="application/json;charset = utf-8",
        status=400,
    )


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def enviroment(request: Request) -> Response:
    """enviroment 获取title，logo等配置
    """
    data = request.domain.config
    data['profileUrl'] = f'{request.domain.hac.url}/account/profile'
    data['hacUrl'] = f'{request.domain.hac.url}'
    data['loginUrl'] = f'{request.domain.url}' + reverse('cas:login')
    data['logoutUrl'] = f'{request.domain.url}' + reverse('cas:logout')
    return Response(data)


@api_view(['GET'])
def profile(request: Request) -> Response:
    try:
        data = dict(name=request.user.username, email=request.user.email)
        data.update(
            avatar=None,
            avatarThumb=None,
            theme=None,
            apps=None
        )
    except AttributeError:
        response = dict(message="未登录或 session 过期", url=f'{request.domain.url}' + reverse('cas:login'))
        return Response(status=401, data=response)

    url = f'{request.domain.hac.url}/api/admin/users/{request.user.hacId}/profile'
    try:
        hacResponse = requests.get(url, timeout=10, headers=request.domain.hac.identify or {'identify': 'URBahpGT5tYCFd0rjy2EHe1oVYX7O3hb'}).json()
    except Exception:
        logger.error(url)
        logger.error(traceback.format_exc())
        hacResponse = {}

    userInfo = hacResponse.get('result', {}) or {'language': settings.LANGUAGE_CODE}
    if userInfo:
        data.update(userInfo)
    request.session[translation.LANGUAGE_SESSION_KEY] = data['language']

    return Response(data)


@api_view(['GET'])
def userSettings(request: Request):
    """重定向到hac的settings"""
    redirectUrl = f'{request.domain.hac.url}/settings'
    return HttpResponseRedirect(redirectUrl)



@api_view(['POST'])
def upload(request):
    path = uuid.uuid4().hex
    myfile = request.FILES.get("file")
    storage = request.GET.get("storage", "")
    ext = ""
    storage_class = default_storage
    if not myfile:
        return Response({"file": 'required'}, status_code=401)
    if "." in myfile.name:
        ext = myfile.name.split(".")[-1]
    path = f"{path}.{ext}"
    if storage:
        storage_class = FileSystemStorage()
        path = myfile.name
    file = storage_class.open(path, "wb")
    file.write(myfile.read())
    file.close()
    url = storage_class.url(path)
    return Response({"file_path": path, "url": url})