import os
from logging import getLogger
from typing import Mapping

from aiohttp import ClientSession, web
from aiohttp.abc import Request
from aiohttp.web_response import Response
from tartiflette import Engine

from .clients import HttpApi, ApiRequest, DBApi
from .config import Config
from .graphiql import set_graphiql_handler
from .resolvers import QueryResolver, MutationResolver, ResolverDec
from .utils import parse_conf, import_module, resolve_paths
from .view import create_endpoint, options_handler

logger = getLogger(__name__)


class GqlExt:
    config: Config

    rest_description = []
    db_description = []
    resolvers_description = []

    def __init__(self, app, path_to_init_file, base_path):
        self.config = Config()
        self.app = app
        self.base_path = base_path
        self.init_conf = parse_conf(path_to_init_file)

        rest_clients_files_path = self.init_conf.get('rest') or []
        for rest_file in rest_clients_files_path:
            self.rest_description.append(parse_conf(os.path.join(base_path, rest_file)))

        db_client_file_path = self.init_conf.get('db') or []
        for db_file in db_client_file_path:
            self.db_description.append(parse_conf(os.path.join(base_path, db_file)))

        self.schemas = self.init_conf.get('schemas') or {}

    def mount_app(self):
        for rest_description in self.rest_description:
            self.set_rest_service(rest_description)
        for db_description in self.db_description:
            self.set_db_service(db_description)

        for schema_name, schema_description in self.schemas.items():
            resolvers_description_file_path = os.path.join(self.base_path, schema_description.get('resolvers'))
            resolvers_description = parse_conf(resolvers_description_file_path)
            self.set_resolvers(resolvers_description, schema_name)

            sdl_paths = [os.path.join(self.base_path, sdl) for sdl in schema_description.get('sdl') or []]
            sdl_paths = resolve_paths(sdl_paths)

            self.mount(schema_name, sdl_paths, schema_description.get('modules'),
                       url=schema_description.get('url'))

        if self.config.allow_cors:
            async def on_prepare(req: Request, res: Response):
                if req.headers.get('ORIGIN'):
                    res.headers['Access-Control-Allow-Origin'] = req.headers.get('ORIGIN')
                res.headers['Access-Control-Allow-Credentials'] = 'true'

            self.app.on_response_prepare.append(on_prepare)

    # REST

    def set_rest_service(self, rest_description):
        rest_clients = self.get_rest_clients(rest_description)

        for service_name, client in rest_clients.items():

            session = ClientSession(raise_for_status=True)

            async def start_rest(app_):
                if not hasattr(app_, 'rest_client'):
                    app_.rest_client = {}
                if not self.config.get_rest(service_name):
                    raise RuntimeError('You must specify the base address of the service')
                service_base_url = self.config.get_rest(service_name)
                if app_.rest_client.get(service_name):
                    raise RuntimeError(f'This name of REST service is already in use {service_name}')

                app_.rest_client[service_name] = await client.create(service_base_url, session=session,
                                                                     proxy_headers=self.config.proxy_headers)

            async def shutdown(app_):
                await session.close()

            self.app.on_startup.append(start_rest)
            self.app.on_shutdown.append(shutdown)

    @staticmethod
    def get_rest_clients(rest_descr: Mapping) -> Mapping:
        res = {}
        for rest_service, endpoints in rest_descr.items():
            class Rest(HttpApi):
                pass

            for k, v in endpoints.items() or []:
                setattr(Rest, k, ApiRequest(method=(v.get('method') or 'GET'), path_template=v['path']))
            res[rest_service] = Rest
        return res

    # DB

    def set_db_service(self, db_description: Mapping):
        db_clients = self.get_db_clients(db_description)

        for db_client_name, client in db_clients.items():
            async def start_db(app_):
                if not hasattr(app_, 'db_client'):
                    app_.db_client = {}
                app_.db_client[db_client_name] = await client.create(**self.config.get_db(db_client_name))

            async def shutdown(app_):
                await app_.db_client[db_client_name].close()

            self.app.on_startup.append(start_db)
            self.app.on_shutdown.append(shutdown)

    @staticmethod
    def get_db_clients(db_description: Mapping) -> Mapping:
        res = {}
        for db_service, endpoints in db_description.items():
            class DB(DBApi):
                pass

            for k, v in endpoints.items() or []:
                setattr(DB, k, import_module(v.get('query'))())
            res[db_service] = DB
        return res

    # SCHEMAS
    @staticmethod
    def parse_arg(arg_value, parent, ctx):
        if not isinstance(arg_value, str):
            return arg_value
        if arg_value.startswith('parent.'):
            return parent.get(arg_value.split('.')[-1])
        if arg_value.startswith('request.'):
            return ctx['request'].get(arg_value.split('.')[-1])
        return arg_value

    def parse_args(self, arg_value, parent, ctx):
        if isinstance(arg_value, (list, tuple)):
            return [self.parse_arg(arg, parent, ctx) for arg in arg_value if arg is not None]
        return self.parse_arg(arg_value, parent, ctx)

    def init_loader(self, args_, inherit_cls):
        async def loader_(_item, parent, args, ctx, info):
            if args_ is not None:
                for arg_name, arg_val in args_.items():
                    arg_val = self.parse_args(arg_val, parent, ctx)
                    if not (arg_val or isinstance(arg_val, bool)):
                        return
                    args.update({arg_name: arg_val})
            return await inherit_cls.load(_item, parent, args, ctx, info)

        return loader_

    def set_resolvers(self, resolvers: dict, schema: str):
        for k, v in resolvers.items():
            inherit_cls = MutationResolver if k.startswith('Mutation.') else QueryResolver

            @ResolverDec(k, schema_name=schema)
            class LoaderIMPL(inherit_cls):
                if v.get('loader'):
                    load = import_module(v.get('loader'))
                else:
                    load = self.init_loader(v.get('args'), inherit_cls)
                if v.get('endpoint'):
                    endpoint = self.get_endpoint(v['endpoint'])
                batch = bool(v.get('batch'))

    def get_endpoint(self, endpoint_name: str) -> str:
        service = endpoint_name.split('.')[0]
        if service not in ['db', 'rest'] and self.config.default_service is not None:
            return f'{self.config.default_service}.{endpoint_name}'
        return endpoint_name

    def mount(self, schema, sdl, modules, url=None):
        allow_cors = self.config.allow_cors
        if not url:
            url = f'/graphql/{schema}'

        async def start(app_, engine=None):
            if engine is None:
                engine = Engine()

            await engine.cook(sdl=sdl, schema_name=schema, modules=modules)
            app_.add_routes([web.post(url, create_endpoint(engine))])
            set_graphiql_handler(app_, True, {'endpoint': url}, url, ['POST'], None)

            if allow_cors:
                app_.add_routes([web.options(url, options_handler)])

            logger.debug(f'{schema} schema has been initialized')

        self.app.on_startup.append(start)
