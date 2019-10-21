from typing import Type
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response


class Integration:
    def __init__(self, name: str) -> None:
        self.name = name

    def inject_middleware(self, app: FastAPI):
        @app.middleware("http")
        async def db_session_middleware(request: Request, call_next):
            response = Response("Internal server error", status_code=500)
            try:
                setattr(request.state, 'i_' + self.name, self)
                response = await call_next(request)
            finally:
                pass
            return response

    def init(self):
        pass

    def load(self):
        pass


class IntegrationManager:
    def __init__(self, app: FastAPI) -> None:
        self.integrations = []
        self.app = app

    def register(self, integration: Integration):
        integration.init()
        integration.inject_middleware(app=self.app)
        self.integrations.append(integration)

    def load(self):
        for integration in self.integrations:
            integration.load()

    def get(self, name: str) -> Type[Integration]:
        for integration in self.integrations:
            if integration.name == name:
                return integration
