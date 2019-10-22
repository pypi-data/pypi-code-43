import unittest
import json
import datetime
import jwt
from base64 import b64encode
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
from gino.ext.aiohttp import Gino
from aiohttp_ext.auth.extension import Auth
from aiohttp_ext.auth.decorators import authorization_required, bearer_authorization_required
from settings import settings


class AioHTTPExtAuthTestCase(AioHTTPTestCase):

    _app = None
    _private_key = None

    @staticmethod
    async def _create_test_db(db, config):
        """Создать тестовую БД. Если БД уже существует, то предварительно удалить ее, а затем создать новую"""

        host = config['gino']['host']
        port = config['gino']['port']
        database = config['gino']['database']
        password = config['gino']['password']
        db_user = config['gino']['user']

        engine = await db.set_bind(f'postgresql://{db_user}:{password}@{host}:{port}/postgres', strategy='gino')

        async with engine.acquire() as conn:
            # Проверяем существование тестовой БД
            if await conn.scalar(f'SELECT count(*) FROM pg_database WHERE datname = \'{database}\''):
                # Тестовая БД уже существует. Удаляем ее
                await conn.scalar(f'DROP DATABASE {database}')

            # Создаем новую БД
            await conn.scalar(f'CREATE DATABASE {database} OWNER {db_user}')

        await db.pop_bind().close()

    async def get_application(self):
        """
        Создать тестовый стенд
        """

        @bearer_authorization_required(
            realm='http://authorization-point:8080/authorization-point/api/v1/token/',
            service='demo_app',
            scope='bearer_auth_handler'
        )
        async def bearer_auth_handler(request):
            return web.json_response(request['jwt_payload'])

        @authorization_required
        async def basic_auth_handler(request):
            return web.json_response({'username': f'{request["user"].username}'})

        db = Gino()

        app = web.Application(middlewares=[db])

        app['config'] = settings

        # Создаем тестовую БД
        await self._create_test_db(db, app['config'])

        db.init_app(app)

        app['auth'] = Auth()
        app['auth'].init_app(app)

        app.router.add_get('/basic-auth-handler', basic_auth_handler)
        app.router.add_get('/bearer-auth-handler', bearer_auth_handler)

        self._app = app

        return app

    async def setUpAsync(self):
        await self._app['db'].gino.create_all()

        # Создаем тестового пользователя
        await self._app['auth'].get_user_model().create(
            username='some_user',
            password='some_password',
        )

        await self._app['auth'].get_user_model().create(
            username='some_user_with_none_password',
            password=None,
        )

        # Загружаем приватный ключ
        with open('id_rsa') as private_key_file:
            self._private_key = private_key_file.read()

    @unittest_run_loop
    async def test_unauthorized_basic_request(self):
        """Тестируем неавторизованный запрос к ресурсу, требующему basic-авторизацию"""

        resp = await self.client.request("GET", "/basic-auth-handler")
        self.assertEquals(resp.status, 401)
        self.assertTrue('Учетные данные не были предоставлены.' in await resp.text())

    @unittest_run_loop
    async def test_authorized_basic_request(self):
        """Тестируем авторизованный запрос к ресурсу, требующему basic-авторизацию"""

        auth = b64encode(b"some_user:some_password").decode("ascii")

        resp = await self.client.request("GET", "/basic-auth-handler", headers={
            'Authorization': f'Basic {auth}'
        })
        self.assertEquals(resp.status, 200)
        self.assertEquals(json.loads(await resp.text())['username'], 'some_user')

        # Пробуем авторизоваться с учетной записью пользователя вообще не имеющего пароля
        auth = b64encode(b"some_user_with_none_password:").decode("ascii")
        resp = await self.client.request("GET", "/basic-auth-handler", headers={
            'Authorization': f'Basic {auth}'
        })
        self.assertEquals(resp.status, 401)
        self.assertTrue('Учетные данные не были предоставлены.' in await resp.text())

    @unittest_run_loop
    async def test_unauthorized_bearer_request(self):
        """Тестируем неавторизованный запрос к ресурсу, требующему bearer-авторизацию"""

        resp = await self.client.request("GET", "/bearer-auth-handler")
        self.assertEquals(resp.status, 401)
        self.assertTrue('Bearer realm="http://authorization-point:8080/authorization-point/api/v1/token/",'
                        'service="demo_app",scope="bearer_auth_handler' in resp.headers['Www-Authenticate'])

    @unittest_run_loop
    async def test_authorized_bearer_request(self):
        """Тестируем авторизованный запрос к ресурсу, требующему bearer-авторизацию"""

        # Тестируем доступ с токеном с логином пользователя известного системе
        token = jwt.encode(
            {'user_id': 'some_user'}, algorithm=self._app['config']['jwt']['algorithm'], key=self._private_key
        ).decode('utf-8')

        resp = await self.client.request("GET", "/bearer-auth-handler", headers={
            'Authorization': f'Bearer {token}'
        })

        self.assertEquals(resp.status, 200)
        self.assertEquals(json.loads(await resp.text())['user_id'], 'some_user')

        # Тестируем доступ с токеном с логином пользователя не известного системе
        token = jwt.encode(
            {'user_id': 'new_user'}, algorithm=self._app['config']['jwt']['algorithm'], key=self._private_key
        ).decode('utf-8')

        resp = await self.client.request("GET", "/bearer-auth-handler", headers={
            'Authorization': f'Bearer {token}'
        })

        self.assertEquals(resp.status, 200)
        self.assertEquals(json.loads(await resp.text())['user_id'], 'new_user')

        # Тестируем доступ с просроченым токеном
        expired_token = jwt.encode(
            {
                'user_id': 'some_user',
                'exp': datetime.datetime(2010, 10, 7, 17, 53, 9, 119745)
            }, algorithm=self._app['config']['jwt']['algorithm'], key=self._private_key
        ).decode('utf-8')

        resp = await self.client.request("GET", "/bearer-auth-handler", headers={
            'Authorization': f'Bearer {expired_token}'
        })

        self.assertEquals(resp.status, 401)
        self.assertEquals(await resp.text(), 'Signature has expired')
        self.assertTrue('Bearer realm="http://authorization-point:8080/authorization-point/api/v1/token/",'
                        'service="demo_app",scope="bearer_auth_handler' in resp.headers['Www-Authenticate'])


if __name__ == '__main__':
    unittest.main()
