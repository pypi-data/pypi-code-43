import unittest
import asyncio
from aiohttp.test_utils import make_mocked_request

from ...handler import newMethod, Endpoint
from ...parsing import json
from ...parsing.fields import BoolField, StringField

from ..test_case import (
    ClericusTestCase,
    unittest_run_loop,
    async_test,
)


class TestMethods(unittest.TestCase):
    @async_test
    async def testMethodCreation(self):
        async def process(self):
            return {"ok": True, "text": "stuff"}

        method = newMethod(
            name="Test Method",
            httpMethod="Get",
            description="This is a test handler",
            process=process,
            responseFields={
                "ok": BoolField(),
                "text": StringField(),
            },
        )

        req = make_mocked_request('GET', '/')

        resp = await method().handle(req)
        respBody = json.loads(resp.body)

        self.assertEqual(respBody["ok"], True)
        self.assertEqual(respBody["text"], "stuff")


class TestUrlParameters(ClericusTestCase):
    async def get_application(self):
        app = await super().get_application()

        async def process(self, value):
            return {"result": value + " cow"}

        getMethod = newMethod(
            name="Test Method",
            httpMethod="Get",
            description="This is a test handler",
            process=process,
            urlParameters={
                "value": StringField(),
            },
            responseFields={
                "result": StringField(),
            },
        )

        class end(Endpoint):
            Get = getMethod

        app.addEndpoint(
            "/stuff/{value}/",
            end,
        )
        return app

    @unittest_run_loop
    async def testParameters(self):
        resp = await self.client.request("GET", "/stuff/moo/")
        self.assertEqual(resp.status, 200)
        data = await resp.json()

        self.assertEqual(data["result"], "moo cow")