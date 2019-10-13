import jwt

from datetime import datetime
from calendar import timegm

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from .settings import app_settings
from . import exceptions


def jwt_payload(user, context=None):
    username = user.get_username()

    if hasattr(username, 'pk'):
        username = username.pk

    payload = {
        user.USERNAME_FIELD: username,
        'exp': datetime.utcnow() + app_settings.JWT_EXPIRATION_DELTA,
    }

    if app_settings.JWT_ALLOW_REFRESH:
        payload['origIat'] = timegm(datetime.utcnow().utctimetuple())

    if app_settings.JWT_AUDIENCE is not None:
        payload['aud'] = app_settings.JWT_AUDIENCE

    if app_settings.JWT_ISSUER is not None:
        payload['iss'] = app_settings.JWT_ISSUER

    return payload

def jwt_encode(payload, context=None):
    return jwt.encode(
        payload,
        app_settings.JWT_SECRET_KEY,
        app_settings.JWT_ALGORITHM,
    ).decode('utf-8')


def jwt_decode(token, context=None):
    return jwt.decode(
        token,
        app_settings.JWT_SECRET_KEY,
        app_settings.JWT_VERIFY,
        options={
            'verify_exp': app_settings.JWT_VERIFY_EXPIRATION,
        },
        leeway=app_settings.JWT_LEEWAY,
        audience=app_settings.JWT_AUDIENCE,
        issuer=app_settings.JWT_ISSUER,
        algorithms=[app_settings.JWT_ALGORITHM])

def get_payload(token, context=None):
    try:
        payload = app_settings.JWT_DECODE_HANDLER(token, context)
    except jwt.ExpiredSignature:
        raise exceptions.JSONWebTokenExpired()
    except jwt.DecodeError:
        raise exceptions.JSONWebTokenError(_('Error decoding signature'))
    except jwt.InvalidTokenError:
        raise exceptions.JSONWebTokenError(_('Invalid token'))
    return payload

def get_user_by_natural_key(username):
    User = get_user_model()
    try:
        return User.objects.get_by_natural_key(username)
    except User.DoesNotExist:
        return None

def get_user_by_payload(payload):
    username = app_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER(payload)

    if not username:
        raise exceptions.JSONWebTokenError(_('Invalid payload'))

    user = app_settings.JWT_GET_USER_BY_NATURAL_KEY_HANDLER(username)

    if user is not None and not user.is_active:
        raise exceptions.JSONWebTokenError(_('User is disabled'))
    return user

def get_user_by_token(token, context=None):
    payload = get_payload(token, context)
    return get_user_by_payload(payload)
