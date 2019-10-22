"""Декораторы"""

from aiohttp import web


def authorization_required(fn):
    """Декоратор требущий любую авторизацию"""
    async def wrapped(request, **kwargs):
        if not request.get("user", False):
            return web.Response(status=401, text='Учетные данные не были предоставлены.')
        return await fn(request, **kwargs)
    return wrapped


def bearer_authorization_required(realm, service='*', scope='*'):
    """Декоратор требующий bearer авторизацию и формирующий заголовок ответа, в случае если она не пройдена
    """
    def wrapper1(fn):
        async def wrapped2(request, **kwargs):
            if not request.get("user", False):
                text_error = request.get('jwt_payload', {}).get('error', 'Учетные данные не были предоставлены.')
                return web.Response(
                    headers={
                        'www-authenticate': f'Bearer realm="{realm}",service="{service}",scope="{scope}"'
                    },
                    status=401,
                    text=text_error
                )
            return await fn(request, **kwargs)
        return wrapped2
    return wrapper1
