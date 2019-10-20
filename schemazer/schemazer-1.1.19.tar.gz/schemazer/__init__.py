from flask import request
from flask_classy import route
from functools import wraps

from schemazer.base import (
    SchemazerParameter, SchemazerHeader, SchemazerCookie,
    SchemazerSystemParameter)
from schemazer.helpers import remote_addr
from schemazer.commons.errors import RequestErrors
from schemazer.config import SchemazerConfig
from schemazer.validator import RequestValidator


class QueryMeta:
    ip = None
    systems = None
    cookies = None
    headers = None

    def __init__(self):
        self.systems = {}
        self.cookies = {}
        self.headers = {}


class Query:
    def __init__(self):
        self.meta = QueryMeta()
        self.args = {}

    def to_dict(self):
        return {
            'args': self.args,
            'cookies': self.meta.cookies,
            'headers': self.meta.headers,
            'systems': self.meta.systems,
        }


class Schemazer:
    def __init__(self, app, schema):
        self.schema = schema
        self.config = SchemazerConfig()

        app.schemazer = self

        for param in [x for x in dir(SchemazerConfig) if
                      not x.startswith('_')]:
            name = 'SCHEMAZER_' + param
            setattr(self.config, param,
                    app.config.get(name, getattr(self.config, param)))

        if not self.config.AUTH_ACCESS_TOKEN:
            raise ValueError('Set AUTH_ACCESS_TOKEN, it`s importantly for '
                             'secure')

    def route(self, schema=None, path=None):
        def decorator(f):
            @route(path if path else schema.path, methods=schema.methods)
            @wraps(f)
            def decorated_function(*args, **kwargs):
                request.query = Query()

                if request.method == 'GET':
                    request.query.args.update(request.args.to_dict(flat=True))
                if request.method == 'POST':
                    data = request.get_json() or dict()
                    if not isinstance(data, dict):
                        return RequestErrors.BadRequest.json_abort()
                    request.query.args.update(data)

                for param in schema.systems or []:
                    request.query.meta.systems[param.name] = (
                            request.query.args.get(param.query_param) or
                            (request.headers or {}).get(param.header_param) or
                            (request.cookies or {}).get(param.cookie_param)
                    )

                request.query.meta.ip = remote_addr(request)
                request.query.meta.cookies = request.cookies
                request.query.meta.headers = request.headers

                request_validator = RequestValidator()
                check_items = {
                    SchemazerParameter: {
                        'values': request.query.args,
                        'schema': schema.parameters
                    },
                    SchemazerHeader: {
                        'values': request.query.meta.headers,
                        'schema': schema.headers
                    },
                    SchemazerCookie: {
                        'values': request.query.meta.cookies,
                        'schema': schema.cookies
                    },
                    SchemazerSystemParameter: {
                        'values': request.query.meta.systems,
                        'schema': schema.systems
                    }
                }

                for check_type, item in check_items.items():
                    result = request_validator.process(
                        parameters=item['schema'],
                        check_type=check_type,
                        **item['values'] or {})

                    if result is not True:
                        return result

                return f(*args, **kwargs)
            return decorated_function
        return decorator
