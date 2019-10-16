import unittest
import asyncio
from aiohttp.test_utils import make_mocked_request

from ...handler import newMethod, Endpoint
from ...handler.testing import HttpTest, TestRequest, TestResponse
from ...parsing import json
from ...parsing.fields import BoolField, StringField, EnumeratedStringField

from ..test_case import (
    ClericusTestCase,
    unittest_run_loop,
    async_test,
)

from ... import Clericus
from ...config import defaultSettings, connectToDB

settings = defaultSettings()
settings["db"]["name"] = f"test{'moo'}"
settings = connectToDB(settings)


# await settings["db"].client.drop_database(settings["db"].name)
# await createCollections(self.db)
async def process(self, exampleValue):
    return {"result": exampleValue + " cow"}


getMethod = newMethod(
    name="Test GET Method",
    httpMethod="Get",
    description="This is a test handler",
    process=process,
    urlParameters={
        "exampleValue": StringField(description="A string to modify", ),
    },
    responseFields={
        "result": StringField(description="The value with \"cow\" appended", ),
    },
    tests=[
        HttpTest(
            request=TestRequest(path="/stuff/moo", ),
            response=TestResponse(
                statusCode=200,
                body=json.dumps({"result": "moo cow"}, indent=1),
            ),
        )
    ]
)


class end(Endpoint):
    """
    An example endpoint.
    """
    Get = getMethod


class myServer(Clericus):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.addEndpoint(
            "/stuff/{exampleValue}/",
            end,
            name="Example Endpoint",
        )


app = myServer(settings, logging=False)

globals().update(app.getTests())
