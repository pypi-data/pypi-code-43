from . import utils
from . import exceptions

def get_token(info):
    auth_header = info.context.META.get('HTTP_AUTHORIZATION')
    return auth_header.split(' ')[-1]

def plugs_ariadne_jwt_middleware(resolver, obj, info, **args):
    try:
        token = get_token(info)
        user = utils.get_user_by_token(token.split(' ')[-1])
        info.context.user = user
    except exceptions.JSONWebTokenError:
        pass
    return resolver(obj, info, **args)
