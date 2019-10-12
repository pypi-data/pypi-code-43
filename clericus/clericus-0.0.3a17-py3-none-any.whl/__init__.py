import json
import markdown

from aiohttp import web
from aiohttp.web_middlewares import normalize_path_middleware
from dataclasses import dataclass, field
from types import SimpleNamespace as SN
from typing import Sequence

from .routes import (
    authentication as authenticationRoutes,
    permissions as permissionRoutes,
    health as healthRoutes,
)
from .config import defaultSettings
from .middleware import (
    logger,
    allowCors,
    removeServerHeader,
    authentication as authenticationMiddleware,
)
from .handler import (
    newMethod,
    Endpoint,
    Method,
)

from .parsing import handleAcceptHeader
from .documentation import requestDocumentationToApiBlueprint


class Clericus(web.Application):
    def __init__(self, settings=None, logging=True, usernameField="username"):
        baseSettings = defaultSettings()
        baseSettings.update(settings or {})
        middlewares = [
            normalize_path_middleware(append_slash=True),
            allowCors(origins=baseSettings["corsOrigins"]),
            removeServerHeader,
        ]

        if logging:
            middlewares.append(logger(usernameField))

        middlewares.append(
            authenticationMiddleware(
                db=baseSettings["db"],
                secretKey=baseSettings["jwtKey"],
            ),
        )
        super().__init__(middlewares=middlewares, )

        self.documentation = []

        self["settings"] = baseSettings

        self.router.add_route(
            "GET",
            "/",
            self.documentationHandler,
        )

        self.addEndpoint(
            "/healthy/",
            healthRoutes.HealthCheckEndpoint,
        )

    def addEndpoint(self, path, handlerClass, name=None):
        cls = handlerClass(
            settings=SN(**self["settings"]),
            name=name,
            path=path,
        )
        self.router.add_route("*", path, cls.handle)
        self.router.add_route(
            "get",
            f"/documentation{path}",
            cls.handleDocumentation,
        )

        self.documentation.append(cls.describe())

    async def documentationHandler(self, request: web.Request) -> web.Response:
        docs = self.describe()

        acceptHeader = request.headers.get("Accept")

        if acceptHeader:
            contentType, _ = handleAcceptHeader(
                acceptHeader,
                [
                    "text/html",
                    "application/json",
                ],
            )
        else:
            contentType = "application/json"

        if contentType == "text/html":
            md = "# Documentation\n"
            for endpoint in docs["endpoints"]:
                md += requestDocumentationToApiBlueprint(endpoint)
            htmlContent = markdown.markdown(md)
            html = f"<html><body>{htmlContent}</body></html>"

            return web.Response(
                text=html,
                headers={"Content-Type": "text/html"},
            )

        else:
            return web.Response(
                text=json.dumps(docs),
                headers={"Content-Type": "application/json"},
            )

    def describe(self):
        return {
            "endpoints": sorted(
                self.documentation,
                key=lambda k: k["path"],
            )
        }

    def runApp(self):
        web.run_app(self)
