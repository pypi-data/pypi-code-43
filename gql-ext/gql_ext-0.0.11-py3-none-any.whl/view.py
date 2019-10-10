import json
from copy import copy

from aiohttp import web
from aiohttp.web import View, Response

from .exceptions import BadRequestError


class GraphQLView(View):
    engine = None

    @staticmethod
    async def parse_params(req):
        try:
            req_content = await req.json(loads=json.loads)
        except Exception:
            raise BadRequestError("Body should be a JSON object")

        if "query" not in req_content:
            raise BadRequestError('The mandatory "query" parameter is missing.')

        variables = None
        if "variables" in req_content and req_content["variables"] != "":
            variables = req_content["variables"]
            try:
                if isinstance(variables, str):
                    variables = json.loads(variables)
            except Exception:
                raise BadRequestError(
                    'The "variables" parameter is invalid. '
                    "A JSON mapping is expected."
                )

        return req_content["query"], variables, req_content.get("operationName")

    async def handle_query(self, req, query, query_vars, operation_name, context):
        context = copy(context)
        try:
            if not operation_name:
                operation_name = None

            return await self.engine.execute(
                query=query,
                variables=query_vars,
                context=context,
                operation_name=operation_name,
            )
        except Exception as e:
            return {"data": None, "errors": str(e)}

    async def post(self):
        if not self.engine:
            raise NotImplementedError
        user_c = {'request': self.request}
        qry, qry_vars, op_name = await self.parse_params(self.request)
        data = await self.handle_query(self.request, qry, qry_vars, op_name, user_c)
        return web.json_response(data, dumps=json.dumps)


async def options_handler(request):
    headers = {'Access-Control-Allow-Methods': 'POST',
               'Access-Control-Allow-Headers': ', '.join(request.headers.values())}
    return Response(headers=headers)


def create_endpoint(_engine):
    class Endpoint(GraphQLView):
        engine = _engine

    return Endpoint
