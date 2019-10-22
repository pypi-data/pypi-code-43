"""Бакэнды http-авторизации"""

import base64
import datetime
import logging

import jwt
from jwt.exceptions import InvalidTokenError

from .exceptions import InvalidConfiguration


class AuthorizationBackend:
    """Абстрактный класс бакэнда HTTP-авторизации"""

    def __init__(self, app):
        self._user_model = app['auth'].get_user_model()

    async def authorization(self, request):
        """Метод проводящий авторизацию пользователя

        В случае успеха, метод должен вернуть экземпляр профиля пользователя, а в случае неудачи - значение None
        """
        raise NotImplemented


class BasicAuthorizationBackend(AuthorizationBackend):
    """Бакэнд Basic авторизации"""

    def __init__(self, app):
        super().__init__(app)

    async def authorization(self, request):
        try:
            auth_data = request.headers.get('Authorization', None)
            auth_data = request.headers.get('AUTHORIZATION', auth_data)

            if not auth_data or not isinstance(auth_data, str):
                return None

            try:
                keyword, auth_data = auth_data.split(' ')
            except ValueError:
                return None

            if keyword != 'Basic':
                return None

            auth_data = base64.b64decode(auth_data)
            auth_data = auth_data.decode()

            username = auth_data.split(':')[0]
            password = auth_data.split(':')[1]
        except IndexError:
            return None

        users = await self._user_model.query.where(
            self._user_model.username == username).gino.all()

        if users and users[0].password == password and users[0].is_active:
            return users[0]

        return None


class BearerAuthorizationBackend(AuthorizationBackend):
    """Бакэнд Bearer авторизации"""

    _last_error = None

    def __init__(self, app):
        self._app = app
        self._config = app['config'].get('jwt', {})

        # Считываем публичный ключ и сохраняем его в экземпляр приложения
        if not self._config.get('pub_key', False):
            raise InvalidConfiguration('Public key is not configured!')

        with open(self._config['pub_key']) as pub_key_file:
            app['jwt_pub_key'] = pub_key_file.read()

        super().__init__(app)

    def _decode_token(self, token, verify=True):
        """Декодировать и проверить токен"""

        try:
            return jwt.decode(
                token,
                key=self._app['jwt_pub_key'],
                algorithms=self._config.get('algorithm', 'RS256'),
                verify=verify
            )
        except InvalidTokenError as e:
            logging.debug(str(e))
            return {'error': str(e)}

    async def _get_or_create_user(self, payload):
        """Создать или обновить учетную запись из данных токена"""

        # Payload должен быть словарем
        if not payload or not isinstance(payload, dict):
            return None

        # В словаре payload должен быть ключ user_id
        if 'user_id' not in payload:
            return None

        # Ключ user_id не может быть None или пустым значением
        if not payload['user_id']:
            return None

        users = await self._user_model.query.where(
            self._user_model.username == payload['user_id']).gino.all()

        if not users:
            # Учетной записи нет, создаем новую по данным из токена
            return await self._user_model.create(
                username=payload.get('user_id'),
                first_name=payload.get('first_name', ''),
                last_name=payload.get('last_name', ''),
                display_name=payload.get('display_name', ''),
                email=payload.get('email', ''),
                is_staff=False,
                is_active=True,
                password=payload.get('password'),
                last_login=datetime.datetime.utcnow()
            )

        # Обновляем учетную запись данными из токена
        user = users[0]
        await self._user_model.update.values(
            username=payload.get('user_id', user.username),
            first_name=payload.get('first_name', user.first_name),
            last_name=payload.get('last_name', user.last_name),
            display_name=payload.get('display_name', user.display_name),
            email=payload.get('email', user.email),
            is_staff=False,
            is_active=True,
            password=None,
            last_login=datetime.datetime.utcnow()
        ).where(id == user.id).gino.status()

        return user

    async def authorization(self, request):
        auth_data = request.headers.get('Authorization', None)
        auth_data = request.headers.get('AUTHORIZATION', auth_data)

        # Заголовок должен быть определен и он должен быть строкой
        if not auth_data or not isinstance(auth_data, str):
            return None

        # Заголовок должен состоять минимум из двух частей разделенных пробелом
        try:
            keyword, token = auth_data.split(' ')
        except ValueError:
            return None

        # Первая часть заголовка должна быть ключевым словом 'Bearer'
        if keyword != 'Bearer':
            return None

        # Парсируем jwt токен
        payload = self._decode_token(token)

        # Добавляем в объект запроса полезную нагрузку токена
        request['jwt_payload'] = payload

        return await self._get_or_create_user(payload)
