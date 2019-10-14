from django.conf import settings
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth import logout as django_logout
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view

from redmin.utils.rsa import decrypt as rsa_decrypt
from redmin.utils import json_response, attr


@api_view(['POST'])
def login(request):
    data = request.data
    username = data.pop("username", None)
    password = data.pop("password", None)
    encrypted = data.pop("encrypted", False)
    if encrypted:
        private_key = attr(settings, 'REMDIN_PRIVATE_KEY')
        if not private_key:
            return json_response({"code": 500, "status": "failed", "detail": "No private key found, please config REMDIN_PRIVATE_KEY"})
        password = rsa_decrypt(password, private_key)
    user = authenticate(request, username=username, password=password)
    if user:
        auth.login(request, user)
        return json_response({"type": "account", "currentAuthority": "admin", "code": 200, "status": "ok"})
    else:
        return json_response({"type": "account", "currentAuthority": "guest", "code": 403, "status": "failed"})


@api_view(['GET'])
def logout(request):
    django_logout(request)
    return json_response({"code": 200})


@api_view(['GET'])
def token(request):
    return json_response({"code": 200, "token": get_token(request=request), "status": "ok"})


@api_view(['GET'])
def profile(request):
    user = request.user
    return json_response({
        "code": 200,
        "status": "ok",
        "name": attr(user, "username", "guest"),
        "title": attr(user, "title", "访客"),
        "avatar": "https://gw.alipayobjects.com/zos/antfincdn/XAosXuNZyF/BiazfanxmamNRoxxVxka.png",
        "userid": attr(user, "id", -1),
        "email": attr(user, "email", "guest@guest.com"),
    })
