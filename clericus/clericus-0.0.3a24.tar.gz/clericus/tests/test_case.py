import faker
import sys
import unittest
import asyncio

sys.path.append(".")
fake = faker.Faker()

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from .. import Clericus
from ..config import defaultSettings, connectToDB
from ..schemas import createCollections
from ..routes import authentication as authenticationRoutes
from ..parsing import json


def async_test(f):
    def wrapper(self):
        return asyncio.run(f(self))

    return wrapper


class ClericusTestCase(AioHTTPTestCase):
    async def tearDownAsync(self):
        await self.db.client.drop_database(self.db.name)

    async def get_application(self) -> Clericus:
        settings = defaultSettings()
        settings["db"]["name"] = f"test{type(self).__name__}"
        settings = connectToDB(settings)
        await settings["db"].client.drop_database(settings["db"].name)
        self._settings = settings
        self.db = settings["db"]
        await createCollections(self.db)
        return Clericus(self._settings, logging=False)


class AuthenticatedClericusTestCase(AioHTTPTestCase):
    async def tearDownAsync(self):
        await self.db.client.drop_database(self.db.name)

    async def get_application(self) -> Clericus:
        settings = defaultSettings()
        settings["db"]["name"] = f"test{type(self).__name__}"
        settings = connectToDB(settings)
        await settings["db"].client.drop_database(settings["db"].name)
        self._settings = settings
        self.db = settings["db"]
        await createCollections(self.db)
        app = Clericus(self._settings, logging=False)

        app.addEndpoint(
            "/sign-up/",
            authenticationRoutes.SignUpEndpoint,
        )
        app.addEndpoint(
            "/log-in/",
            authenticationRoutes.LogInEndpoint,
        )
        app.addEndpoint(
            "/log-out/",
            authenticationRoutes.LogOutEndpoint,
        )
        app.addEndpoint(
            "/me/",
            authenticationRoutes.MeEndpoint,
        )

        return app

    async def login(self, user=None):
        if not user:
            user = {
                "username": fake.user_name(),
                "email": fake.email(),
                "password": fake.password(),
            }
            resp = await self.client.request(
                "POST",
                "/sign-up/",
                json=user,
            )
        else:
            resp = await self.client.request(
                "POST",
                "/log-in/",
                json=user,
            )
        return user

    async def logout(self):
        resp = await self.client.request(
            "GET",
            "/log-out/",
        )
        return None