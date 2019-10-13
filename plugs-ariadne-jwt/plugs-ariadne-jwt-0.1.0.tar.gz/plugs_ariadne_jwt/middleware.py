from . import utils

def plugs_ariadne_jwt_middleware(resolver, obj, info, **args):
    try:
        token = info.context.headers['Authorization']
        user = utils.get_user_by_token(token.split(' ')[-1])
        info.context.user = user
    except KeyError:
        pass
    return resolver(obj, info, **args)
