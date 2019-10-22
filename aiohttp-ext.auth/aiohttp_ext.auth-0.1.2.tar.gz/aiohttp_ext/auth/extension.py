"""Расширение aiohttp для добавления функционала управления профилями пользователей
 и процессом авторизации их в системе"""

import datetime
from importlib import import_module

from sqlalchemy_utils.types import EmailType, PasswordType
from aiohttp import web

from .exceptions import InvalidConfiguration


class Auth:

    _app = None
    _user_model = None
    _config = None
    _backends = []

    @staticmethod
    def _dynamic_import_class(name):
        module_name = '.'.join(name.split('.')[:-1])
        class_name = '.'.join(name.split('.')[-1:])
        module = import_module(module_name)
        return getattr(module, class_name)

    @web.middleware
    async def _middleware(self, request, handler):
        user = None
        for backend in self._backends:
            user = await backend.authorization(request)
            if user:
                break

        request['user'] = user

        return await handler(request)

    def _init_db_user_model(self, db):
        class User(db.Model):
            __tablename__ = 'users'

            id = db.Column(db.Integer(), primary_key=True, autoincrement='auto')
            username = db.Column(db.String(150), index=True, nullable=False, unique=True)
            first_name = db.Column(db.String(30), default='')
            last_name = db.Column(db.String(150), default='')
            display_name = db.Column(db.String(255), default='')
            email = db.Column(EmailType)
            is_staff = db.Column(db.Boolean, server_default='false', default=False, nullable=False)
            is_active = db.Column(db.Boolean, server_default='true', default=True, nullable=False)
            date_joined = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
            password = db.Column(PasswordType(schemes=['pbkdf2_sha512']))
            last_login = db.Column(db.DateTime(timezone=True))

            def __repr__(self):
                return '{}<{}>'.format(self.username, self.id)

        return User

    def get_user_model(self):
        return self._user_model

    def init_app(self, app):
        app['auth'] = self

        self._app = app
        self._config = app['config'].get('auth', {})

        # Получаем и сохраняем модель профиля пользователя
        if self._config.get('user_model', None):
            self._user_model = self._dynamic_import_class(self._config['user_model'])
        else:
            try:
                self._user_model = self._init_db_user_model(app['db'])
            except IndexError:
                raise InvalidConfiguration('Database is not configured!')

        # Перечисляем доступные бакэенды авторизации
        self._backends = [
            self._dynamic_import_class(backend)(self._app) for backend in self._config.get(
                'auth_backends', [])
        ]

        app.middlewares.append(self._middleware)
