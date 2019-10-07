"""
Station server setup
"""

from __future__ import annotations

import logging
import threading
from http.server import HTTPServer

import flask
from flask import Flask
from werkzeug.serving import make_server
from werkzeug.utils import find_modules
from werkzeug.utils import import_string

from healer.config import CONFIG

from . import config
from . import plugin
from .area.user.model import setup_admin

logger = logging.getLogger(__name__)


class FlaskBuilder:
    """
    Flask application builder
    """

    @staticmethod
    def produce_app(config:config.Config=config.ProdConfig) -> Flask:

        app = Flask(
            __name__,
            static_folder="asset/static",
            template_folder="asset/template",
        )

        app.config.from_object(config)

        app.jinja_env.trim_blocks = True
        app.jinja_env.lstrip_blocks = True

        app.jinja_env.globals['brython_config'] = app.config['BRYTHON_CONFIG']

        app.extensions['tokenizer_blacklist'] = set()

        FlaskBuilder.register_plugin(app)
        FlaskBuilder.register_blueprint(app)

        with app.app_context():
            FlaskBuilder.configure_database()

        return app

    @staticmethod
    def configure_database() -> None:
        setup_admin()

    @staticmethod
    def register_plugin(app:Flask) -> None:
        for entry in plugin.registration_list:
            entry.init_app(app)
        plugin.login.login_view = 'user.ara_login'

    @staticmethod
    def register_blueprint(app:Flask) -> None:
        origins = app.config.get('CORS_ORIGIN_WHITELIST', '*')
        package_list = app.config.get('BLUEPRINT_PACKAGE_LIST')
        for package in package_list:
            for name in find_modules(package, recursive=True):
                module = import_string(name)
                if hasattr(module, 'blueprint'):
                    blueprint = module.blueprint
                    app.register_blueprint(blueprint)
                    plugin.cors.init_app(blueprint, origins=origins)


class FlaskServer(
        threading.Thread,
    ):
    """
    Flask server component
    """

    app:Flask
    private:HTTPServer
    flask_context:flask.ctx.AppContext

    def __init__(self, app:flask.Flask):
        super().__init__()
        self.app = app
        config = CONFIG['station/server']
        host = config['host']
        port = config['port']
        self.private = make_server(
            app=app,
            host=host,
            port=port,
            threaded=True,
        )
        self.flask_context = app.app_context()
        self.flask_context.push()

    def run(self):
        self.private.serve_forever()

    def start(self):
        logger.info(f"startup")
        super().start()

    def stop(self):
        logger.info(f"shutdown")
        self.private.shutdown()


class FlaskSupport:

    @staticmethod
    def produce_server() -> FlaskServer:
        "flask server factory"
        app = FlaskBuilder.produce_app()
        return FlaskServer(app)
