import os

from flask import Flask

from .config import read_configs
from .rule import register_rules, register_exceptions


def create_app(debug=False, configuration=""):
    app = Flask(__name__)
    app.debug = debug
    register_rules(app)
    register_exceptions(app)
    read_configs(app, os.path.join(os.getcwd(), configuration))
    return app
