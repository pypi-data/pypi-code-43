import unittest
import asyncio

from aiohttp.test_utils import make_mocked_request

from ...parsing import json

from ...handler import newMethod, Endpoint
from ...parsing.fields import BoolField, StringField, EnumeratedStringField
from ...handler.testing import HttpTest, TestRequest, TestResponse

from ..test_case import (
    ClericusTestCase,
    unittest_run_loop,
    async_test,
)


class TestDocumentation(ClericusTestCase):
    async def get_application(self):
        app = await super().get_application()

        async def process(self, exampleValue, q=""):
            return {"result": exampleValue + " cow" + q}

        getMethod = newMethod(
            name="Test GET Method",
            httpMethod="Get",
            description="This is a test handler",
            process=process,
            urlParameters={
                "exampleValue": StringField(
                    description="A string to modify",
                ),
            },
            queryParameters={
                "q": StringField(
                    description="A query parameter",
                    optional=True,
                ),
                "moo": StringField(
                    description="Another query parameter",
                    optional=False,
                    default="moo",
                ),
            },
            responseFields={
                "result": StringField(
                    description="The value with \"cow\" appended",
                ),
            },
            tests=[
                HttpTest(
                    request=TestRequest(path="/stuff/moo?q=!", ),
                    response=TestResponse(
                        statusCode=200,
                        body=json.dumps({"result": "moo cow!"}, indent=2),
                    ),
                )
            ]
        )

        postMethod = newMethod(
            name="Test POST Method",
            httpMethod="Post",
            description="This is a test post handler",
            process=process,
            urlParameters={
                "exampleValue": StringField(
                    description="A string to modify",
                ),
            },
            bodyParameters={
                "q": StringField(
                    description="A body parameter",
                    optional=True,
                ),
                "animal": EnumeratedStringField(
                    description="An enumerated parameter",
                    optional=False,
                    default="cow",
                    allowedValues=[
                        "cow",
                        "chicken",
                        "pig",
                    ]
                ),
            },
            responseFields={
                "result": StringField(
                    description="The value with \"cow\" appended",
                ),
            },
        )

        class end(Endpoint):
            """
            An example endpoint.
            """
            Get = getMethod
            Post = postMethod

        app.addEndpoint(
            "/stuff/{exampleValue}/",
            end,
            name="Example Endpoint",
        )
        return app

    @unittest_run_loop
    async def testBaseDocumentationJson(self):
        resp = await self.client.request("GET", "/")
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        endpoints = data["endpoints"]
        self.assertGreater(len(endpoints), 1)

        data = next(
            filter(lambda k: k["path"] == "/stuff/{exampleValue}/", endpoints)
        )
        self.assertEqual(data["description"], "An example endpoint.")
        self.assertEqual(data["name"], "Example Endpoint")
        self.assertEqual(data["path"], "/stuff/{exampleValue}/")
        self.assertEqual(
            data["methods"]["get"]["description"],
            "This is a test handler",
        )

        self.assertEqual(
            data["methods"]["get"]["requestParameters"]["url"]["exampleValue"]
            ["description"],
            "A string to modify",
        )

    @unittest_run_loop
    async def testBaseDocumentationHtml(self):
        resp = await self.client.request(
            "GET",
            "/",
            headers={
                "Accept": "text/html",
            },
        )
        self.assertEqual(resp.status, 200)
        data = await resp.text()

    @unittest_run_loop
    async def testEndpointDocumentationJson(self):
        resp = await self.client.request("GET", "/documentation/stuff/moo/")
        self.assertEqual(resp.status, 200)
        data = await resp.json()

        self.assertEqual(data["description"], "An example endpoint.")
        self.assertEqual(data["name"], "Example Endpoint")
        self.assertEqual(data["path"], "/stuff/{exampleValue}/")
        self.assertEqual(
            data["methods"]["get"]["description"],
            "This is a test handler",
        )

        self.assertEqual(
            data["methods"]["get"]["requestParameters"]["url"]["exampleValue"]
            ["description"],
            "A string to modify",
        )

    @unittest_run_loop
    async def testEndpointDocumentationHtml(self):
        resp = await self.client.request(
            "GET",
            "/documentation/stuff/moo/",
            headers={
                "Accept": "text/html",
            },
        )
        self.assertEqual(resp.status, 200)
        data = await resp.text()
