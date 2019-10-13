from . import utils

def login_required(function):
    def wrapper(*args, **kwargs):
        info = args[1]
        token = info.context.headers['Authorization']
        user = utils.get_user_by_token(token.split(' ')[-1])
        info.context.user = user
        return function(*args, **kwargs)

    return wrapper
