import unittest
import mock
import os
from memex_client.client import BrainiacClient, BRAINIAC_CLIENT_USERNAME, BRAINIAC_CLIENT_PASSWORD
from memex_client.protos.brainiac_pb2 import (BrainiacRequest, BrainiacResponse, Status,
                                              ThirdPartyRequest, ThirdPartyResponse)
from google.protobuf.struct_pb2 import Struct


class MockStub:
    def __init__(self, channel):
        # self.runFunction = self.runfunc
        pass

    def runFunction(self, request: BrainiacRequest) -> BrainiacResponse:
        body = Struct()
        body.update({
            "response": {
                "function_name": request.function_name,
                "force_download": request.force_download,
                "project": {
                    "creator": request.project.creator,
                    "name": request.project.name
                },
                "client": {
                    "username": request.client.username,
                    "password": request.client.password
                },
                "body": request.body["number"]
            }
        })
        return BrainiacResponse(status=Status(status_code=200), body=body)

    def listFunctions(self, request: BrainiacRequest) -> BrainiacResponse:
        body = Struct()
        body.update({"response": ["some_function"]})
        return BrainiacResponse(status=Status(status_code=200), body=body)

    def thirdPartyFunction(self, request: ThirdPartyRequest) -> ThirdPartyResponse:
        body = Struct()
        body.update({
            "response": {
                "function_name":
                request.function_name,
                "module":
                request.module,
                "force_download":
                request.force_download,
                "project": [{
                    "creator": project.creator,
                    "name": project.name
                } for project in request.projects],
                "client": {
                    "username": request.client.username,
                    "password": request.client.password
                },
                "body": request.body["number"]
            }
        })
        return ThirdPartyResponse(status=Status(status_code=200), body=body)


class TestServer(unittest.TestCase):
    @mock.patch.dict(os.environ, {
        BRAINIAC_CLIENT_USERNAME: "username",
        BRAINIAC_CLIENT_PASSWORD: "password"
    })
    def test_CreateFunction(self):
        stub = MockStub(None)
        client = BrainiacClient(stub=stub)
        model = client.get_model_client("testUser0", "testProject0")
        response = model.some_function({"number": 10})
        expected_response = Struct()
        expected_response.update({
            "response": {
                "function_name": "some_function",
                "force_download": False,
                "project": {
                    "creator": "testUser0",
                    "name": "testProject0"
                },
                "client": {
                    "username": 'username',
                    "password": 'password'
                },
                "body": 10
            }
        })
        assert response == expected_response

    @mock.patch.dict(os.environ, {
        BRAINIAC_CLIENT_USERNAME: "username",
        BRAINIAC_CLIENT_PASSWORD: "password"
    })
    def test_ThirdPartyFunction(self):
        stub = MockStub(None)
        client = BrainiacClient(stub=stub)
        model = client.get_model_client("testUser0", "testProject0")
        response = client.runThirdPartyFunction([model], "memex_client.tests.third_party", "action",
                                                {"number": 10})
        expected_response = Struct()
        expected_response.update({
            "response": {
                "function_name": "action",
                "module": "memex_client.tests.third_party",
                "force_download": False,
                "project": [{
                    "creator": "testUser0",
                    "name": "testProject0"
                }],
                "client": {
                    "username": "username",
                    "password": "password"
                },
                "body": 10
            }
        })
        assert response == expected_response
