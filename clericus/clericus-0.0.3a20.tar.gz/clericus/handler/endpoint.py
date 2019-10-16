import markdown

from aiohttp import web
from inspect import getdoc

from .method import Method, newMethod
from ..parsing import handleAcceptHeader, json
from ..documentation import requestDocumentationToApiBlueprint


class Endpoint():
    def __init__(
        self,
        name: str,
        settings=None,
        path: str = None,
    ):
        self.settings = settings or {}
        self.Options = self.generateOptionsClass(
            list(self.methods().keys()) + ["options"],
            settings=self.settings,
        )

        if hasattr(self, "Get"):
            # print(f"Should build HEAD route for {self}")
            self.Head = self.generateHeadClass(
                self.Get,
                settings=self.settings,
            )

        self.name = name
        self.path = path

    def methods(self):
        return {
            f.lower(): self.__getattribute__(f)
            for f in dir(self)
            if isinstance(self.__getattribute__(f), Method.__class__)
            and f[0] != "_"
        }

    async def handle(self, request: web.Request) -> web.Response:
        method = self.methods().get(request.method.lower(), None)
        if method:
            return await method(settings=self.settings).handle(request)
        else:
            return await self.methodNotAllowedHandler(method)

    async def methodNotAllowedHandler(self, method):
        return web.json_response(
            {"errors": ["Method not allowed"]},
            status=405,
        )

    async def handleDocumentation(
        self, request: web.Request, *args
    ) -> web.Response:
        docs = self.describe()
        acceptHeader = request.headers.get("Accept")

        if acceptHeader:
            contentType, _ = handleAcceptHeader(
                acceptHeader,
                [
                    "application/json",
                    "text/html",
                ],
            )
        else:
            contentType = "application/json"

        if contentType == "text/html":
            md = requestDocumentationToApiBlueprint(docs)
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
        docs = {
            "description": getdoc(self),
        }

        if self.name:
            docs["name"] = self.name

        if self.path:
            docs["path"] = self.path

        docs["methods"] = {
            methodName: methodClass("").describe()
            for methodName, methodClass in self.methods().items()
        }
        return docs

    def getTests(self):
        tests = []
        for method in self.methods().values():
            tests += method(settings=self.settings).getTests()
        return tests

    def generateOptionsClass(self, methods, settings=None):
        methodString = ", ".join([m.upper() for m in methods])

        settings = settings or {}

        async def process(self, **kwargs):
            self.setHeader("Allow", methodString)

            # CORS
            self.setHeader("Access-Control-Request-Method", methodString)
            return

        name = getattr(self, 'name', 'Unknown Handler')

        return newMethod(
            name="Options",
            httpMethod="OPTIONS",
            description=
            f"Returns possible methods and content types for this endpoint.",
            process=process,
        )

    def generateHeadClass(self, getMethod, settings):
        class Head(Method):
            """
            HEAD Handler
            """
            name = "Head"
            description = "Returns the same response as a get, but with no body."
            Parser = getMethod.Parser
            process = getMethod.process

            async def serialize(self, result):
                return await self.Serializer().serialize(
                    result,
                    statusCode=self.statusCode,
                    headers=self.headers,
                    cookies=self.cookies,
                    deletedCookies=self.deletedCookies,
                    dropBody=True,
                )

        return Head
