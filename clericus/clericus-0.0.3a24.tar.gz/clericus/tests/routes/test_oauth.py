import unittest
import faker

from aiohttp.test_utils import unittest_run_loop

from ..test_case import ClericusTestCase
from ...routes.authentication import generateOAuthEndpoint

fake = faker.Faker()


class OAuthTestCase(ClericusTestCase):
    async def get_application(self):
        app = await super().get_application()

        return app

    @unittest_run_loop
    async def testOauth(self):

        # print(self.app)

        resp = await self.client.request("GET", "/oauth/test/")
        # self.assertEqual(resp.status, 401)
        # data = await resp.json()
        # print(resp)
        # print(data)