import atexit
import os
from typing import Dict, List, Optional

import grpc
from google.protobuf.struct_pb2 import Struct

from memex_client.protos.brainiac_pb2 import (BrainiacRequest, ProjectData, ThirdPartyRequest,
                                              UserData)
from memex_client.protos.brainiac_pb2_grpc import EngineStub
from memex_client.errors import AuthenticationError

BRAINIAC_CLIENT_USERNAME = "BRAINIAC_CLIENT_USERNAME"
BRAINIAC_CLIENT_PASSWORD = "BRAINIAC_CLIENT_PASSWORD"
DEFAULT_PORT = 5000


class ModelClient:
    def __init__(self, grpc_stub, client, project, force_download):
        self.stub = grpc_stub
        self.client = client
        self.project = project
        self.force_download = force_download

    def set_methods(self, methods: List[str]):
        [setattr(self, method, self.__create_method(method)) for method in methods]

    def __create_method(self, name: str):
        def wrapper(body: Dict):
            struct = Struct()
            struct.update(body)
            response = self.stub.runFunction(
                BrainiacRequest(client=self.client,
                                project=self.project,
                                function_name=name,
                                body=struct,
                                force_download=self.force_download))
            if response.status.status_code == 200:
                return response.body
            return None

        return wrapper


class BrainiacClient:
    def __init__(self, url: Optional[str] = None, stub: EngineStub = None):
        if url is None:
            url = 'localhost:{}'.format(DEFAULT_PORT)
        self.channel = grpc.insecure_channel(url)
        self.stub = stub or EngineStub(self.channel)

        self.client = UserData(username=os.environ.get(BRAINIAC_CLIENT_USERNAME),
                               password=os.environ.get(BRAINIAC_CLIENT_PASSWORD))
        atexit.register(self.channel.close)

    def get_model_client(self, creator: str, project: str,
                         force_download=False) -> Optional[ModelClient]:
        project_data = ProjectData(creator=creator, name=project)
        response = self.stub.listFunctions(BrainiacRequest(client=self.client,
                                                           project=project_data))
        if response.status.status_code == 200:
            methods = response.body["response"]
            model = ModelClient(self.stub, self.client, project_data, force_download)
            model.set_methods(methods)
            return model
        elif response.status.status_code == 404:
            return None
        elif response.status.status_code == 401:
            raise AuthenticationError(response.status.status_reason)
        else:
            raise Exception(response.status.status_reason)

    def runThirdPartyFunction(self,
                              models: ModelClient,
                              module_name,
                              method_name,
                              data: Dict,
                              force_download=False) -> Dict:
        ThirdPartyRequest()
        body = Struct()
        body.update(data)
        response = self.stub.thirdPartyFunction(
            ThirdPartyRequest(client=self.client,
                              projects=[model.project for model in models],
                              function_name=method_name,
                              module=module_name,
                              body=body,
                              force_download=force_download))
        if response.status.status_code == 200:
            return response.body
        return None
