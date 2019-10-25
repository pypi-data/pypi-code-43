from ..parsing import json

from aiohttp.test_utils import AioHTTPTestCase
from dataclasses import dataclass, field

from ..tests.test_case import unittest_run_loop


@dataclass
class TestRequest():
    path: str
    method: str = "GET"
    headers: dict = field(default_factory=dict)
    cookies: dict = field(default_factory=dict)
    body: str = None


@dataclass
class TestResponse():
    statusCode: int
    message: str = ""
    headers: dict = field(default_factory=dict)
    body: str = None


class HttpTest():
    def __init__(
        self,
        request,
        response,
        setUpAsync=None,
        tearDownAsync=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.request = request
        self.response = response
        self.setUpAsync = setUpAsync
        self.tearDownAsync = tearDownAsync

    def generateTestCase(self, appClass, settings):
        expectedRequest = self.request
        expectedResponse = self.response

        theSettings = settings

        class TestCase(AioHTTPTestCase):
            _setUpAsync = self.setUpAsync
            _tearDownAsync = self.tearDownAsync
            settings = theSettings

            async def get_application(self):
                return appClass(settings, logging=False)

            async def compareResponses(self, expected, received):
                if expected.statusCode is not None:
                    self.assertEqual(
                        expectedResponse.statusCode,
                        received.status,
                    )
                if expected.body is not None:
                    receivedBody = await received.text()
                    # check json contents, rather than raw equality
                    if "application/json" in received.headers.get(
                        "Content-Type"
                    ):
                        expectedJson = json.loads(expected.body)
                        receivedJson = json.loads(receivedBody)
                        self.assertDictEqual(expectedJson, receivedJson)
                    else:
                        self.assterEqual(expected.body, receivedBody)

            @unittest_run_loop
            async def testRequest(self):
                if self._setUpAsync is not None:
                    await self._setUpAsync()
                response = await self.client.request(
                    method=expectedRequest.method,
                    path=expectedRequest.path,
                    data=expectedRequest.body,
                    headers=expectedRequest.headers,
                )
                await self.compareResponses(
                    expectedResponse,
                    response,
                )
                return

        return TestCase