from aiohttp import web
from typing import Dict, List

from .fields import Field, ListField, ErrorField
from .errors import ParseError
from ..errors import ClientError, ErrorList
import datetime
import inspect

from . import json


class DictParser():
    def __init__(self, settings=None, *args, **kwargs):
        self.settings = settings or {}
        return

    async def _parse_body(self, request):
        try:
            return json.loads(await request.text())
        except Exception as e:
            print(e)
            return {}

    def _getFields(self):
        return {
            f: theField
            for (f, theField) in filter(
                lambda k: isinstance(k[1], Field),
                inspect.getmembers(self),
            )
        }

    async def parse(self, source: Dict):
        parameters = {}
        errors = []
        for name, parameter in self._getFields().items():
            try:
                if name not in source:
                    if (not parameter.optional):
                        raise ParseError(
                            message="Missing required field: {}".format(name),
                            statusCode=parameter.missingStatusCode,
                        )
                    else:
                        parameters[name] = parameter.default
                else:
                    parameters[name] = parameter.parse(
                        source.get(name, parameter.default)
                    )
            except Exception as err:
                errors.append(err)
        if errors:
            raise ErrorList(errors)
        return parameters

    def describe(self):
        return {
            key: field.describe()
            for (key, field) in self._getFields().items()
        }


class RequestParser():
    BodyParser = DictParser
    QueryParser = DictParser
    CookiesParser = DictParser
    HeadersParser = DictParser
    UrlParser = DictParser

    def __init__(self, *args, **kwargs):
        self.settings = kwargs.get("settings", None)
        return

    async def _parse_body(self, request):
        try:
            if request.can_read_body:
                return await request.json()
            return None
        except Exception as e:
            print(e)
            raise ParseError(message="Unable to parse body")

    async def parse(self, request):
        parameters = {}
        errors = []

        if self.BodyParser:
            body = (await self._parse_body(request)) or {}
            try:
                parameters.update(await self.BodyParser().parse(body))
            except ErrorList as errs:
                errors += errs.errors

        if self.QueryParser:
            try:
                parameters.update(
                    await self.QueryParser().parse(request.query)
                )
            except ErrorList as errs:
                errors += errs.errors

        if self.HeadersParser:
            try:
                parameters.update(
                    await self.HeadersParser().parse(request.headers)
                )
            except ErrorList as errs:
                errors += errs.errors

        if self.CookiesParser:
            try:
                parameters.update(
                    await self.CookiesParser(settings=self.settings, ).parse(
                        request.cookies
                    )
                )
            except ErrorList as errs:
                errors += errs.errors

        try:
            parameters.update(
                await self.UrlParser(settings=self.settings, ).parse(
                    request.match_info
                )
            )

        except:
            raise ClientError(statusCode=404)

        if errors:
            raise ErrorList(errors)

        return parameters

    def describe(self):
        """
        Return a dictionary of possible parameters to be parsed
        """
        description = {
            "body": self.BodyParser().describe(),
            "url": self.UrlParser().describe(),
            "query": self.QueryParser().describe(),
        }

        for (k, v) in list(description.items()):
            if not v:
                del description[k]

        return description


class ResponseSerializer():
    def __init__(self, *args, **kwargs):
        return

    def _getFields(self):
        return {
            f: self.__getattribute__(f)
            for f in dir(self)
            if isinstance(self.__getattribute__(f), Field)
        }

    def makeResponse(self, body, statusCode, headers):
        """
        Convert a parsed body, statusCode, and headers into
        an aiohttp.web.Response
        """
        if body != None:
            response = web.json_response(
                body,
                status=statusCode,
                headers=headers or {},
            )
        else:
            response = web.Response(
                None,
                status=statusCode,
                headers=headers or {},
            )

        return response

    def parseResult(self, result):
        """
        Walk the list of fields and convert them into a(stinrg)
        dictionary ready to be passed to self.makeResponse
        """
        body = {}
        fields = self._getFields()
        for name, resultField in fields.items():

            if hasattr(resultField, "default"):
                value = result.get(name, resultField.default)
            else:
                value = result[name]

            try:
                value = resultField.serialize(value)
            except Exception as e:
                print(e)
                pass

            serializeTo = getattr(resultField, "serializeTo", name) or name
            body[serializeTo] = value
        return body

    def writeCookies(
        self,
        response,
        cookies=None,
        deletedCookies=None,
    ):
        """
        Add/delete cookies to/from a response
        """
        for c in (cookies or {}).values():
            try:
                value = c["value"].decode("utf")
            except:
                value = c["value"]

            kwargs = {
                "name": c["name"],
                "value": value,
                "secure": c["secure"],
                "httponly": c["httpOnly"],
                "expires": c.get(
                    "expires",
                    datetime.datetime.utcnow() + datetime.timedelta(days=1)
                )
            }

            if c.get("domain", None):
                kwargs["domain"] = c["domain"]

            response.set_cookie(**kwargs)

        for c in (deletedCookies or {}).values():
            response.del_cookie(c["name"], domain=c.get("domain", None))

        return response

    async def serialize(
        self,
        result,
        statusCode=200,
        headers=None,
        cookies=None,
        deletedCookies=None,
        dropBody=False,
    ):
        body = self.parseResult(result)
        headers = headers or {}
        headers = {k: "; ".join(vs) for k, vs in headers.items()}

        response = self.makeResponse(
            body=(body if not dropBody else None),
            statusCode=statusCode,
            headers=headers,
        )

        response = self.writeCookies(
            response=response,
            cookies=cookies,
            deletedCookies=deletedCookies,
        )

        return response

    def describe(self):
        return {
            "body": {
                key: field.describe()
                for (key, field) in self._getFields().items()
            }
        }


class ResponseSerializerWithErrors(ResponseSerializer):
    errors = ListField(ErrorField)


class HtmlResponseSerializer(ResponseSerializer):
    def __init__(self, render=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.render = render

    def parseResult(self, result):
        if self.render:
            return self.render(result)
        return result

    def makeResponse(self, body, statusCode, headers):
        return web.Response(
            body,
            status=statusCode,
            headers=headers,
        )


def handleAcceptHeader(
    header: str,  # the header value
    serverTypes: List[str],
) -> str:
    """
    Given the value of an HTTP request Accept header and a list
    of possible types the server supports, and any requested parameters
    """
    clientTypes = [h.strip() for h in header.split(",")]
    clientTypesWithParameters = []
    for ii, t in enumerate(clientTypes[::-1]):
        contentType, *parameters = t.split(";")
        contentType = contentType.strip().lower()

        parameters = [p.strip() for p in parameters]
        parsedParameters = {}
        quality = 1.0
        for p in parameters:
            key, *value = p.split("=")
            value = "=".join(value).strip()
            if key == "q":
                try:
                    quality = float(value)
                except:
                    raise ParseError(
                        message="Invalid Accept Parameter, q must be a number",
                    )
            parsedParameters[key] = value

        clientTypesWithParameters.append({
            "contentType": contentType,
            "quality": (quality, ii),
            "parameters": parsedParameters,
        })

    clientTypesWithParameters = sorted(
        clientTypesWithParameters,
        key=lambda k: k["quality"],
        reverse=True,
    )

    for t in clientTypesWithParameters:
        contentType = t["contentType"]
        parameters = t["parameters"]
        if contentType == "*/*":
            return serverTypes[0], parameters
        elif contentType.endswith("/*"):
            for serverType in serverTypes:
                if serverType.startswith(contentType[:-1]):
                    return serverType, parameters

        elif contentType in serverTypes:
            return contentType, parameters

    return None, None