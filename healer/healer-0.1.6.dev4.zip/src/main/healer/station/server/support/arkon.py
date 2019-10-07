"""
Base plugin types
"""

from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import Blueprint
from flask import Flask
from flask import Markup
from flask import g
from flask import jsonify
from flask import request
from flask import url_for
from flask_jwt_extended import get_jwt_identity
from jsonschema import ValidationError
from jsonschema import validate


def validate_json(schema:str, force:bool=False):

    def decorator(endpoint_function:Callable) -> Callable:

        @wraps(endpoint_function)
        def decorated_function(*args, **kwargs):
            data = request.get_json(force=force)
            if data is None:
                return jsonify(message="need json"), 400
            try:
                validate(data, schema)
            except ValidationError as error:
                return jsonify(message=error.message), 400
            g.data = data
            return endpoint_function(*args, **kwargs)

        return decorated_function

    return decorator


def validate_guid(present:bool):

    def decorator(endpoint_function:Callable) -> Callable:

        @wraps(endpoint_function)
        def decorated_function(*args, **kwargs):
            guid = get_jwt_identity()
            if present and not guid:
                return jsonify(message="need guid"), 400
            if not present and guid:
                return jsonify(message="need no guid"), 400
            g.guid = guid
            return endpoint_function(*args, **kwargs)

        return decorated_function

    return decorator


class PackageResourceExt:
    "load resource from python package"

    def __init__(self,
            # identity
            base_path:str,
            # python package name
            import_name:str,
            # empty means load from import_name root folder
            static_path:str="",
        ):
        self.base_path = base_path
        self.import_name = import_name
        self.static_path = static_path

    def init_app(self, app:Flask) -> None:
        assert not self.base_path in app.extensions, f"need solo: {self.base_path}"
        assert not self.base_path in app.jinja_env.globals, f"need solo: {self.base_path}"
        # flask resolves resources from import_name/static_folder
        blueprint = Blueprint(
            name=self.base_path,
            import_name=self.import_name,
            static_folder=self.static_folder(),
            static_url_path=f'/{self.base_path}',
        )
        app.register_blueprint(blueprint)
        app.extensions[self.base_path] = self
        app.jinja_env.globals[self.base_path] = self

    def static_folder(self) -> str:
        return self.static_path

    def load_script(self, filename:str, mimetype:str) -> Markup:
        # flask maps this key to blueprint static folder
        endpoint = f'{self.base_path}.static'
        load_src = url_for(endpoint=endpoint, filename=filename)
        load_line = f'<script type="{mimetype}" src="{load_src}"></script>'
        return Markup(load_line)

    def load_module(self, filename:str) -> Markup:
        "include es6 module"
        return self.load_script(filename, "module")

    def load_js(self, filename:str) -> Markup:
        "include plain javascript"
        return self.load_script(filename, "text/javascript")

    def load_py(self, filename:str) -> Markup:
        "include plain python code"
        return self.load_script(filename, "text/python")

    def load_css(self, filename:str) -> Markup:
        "include plain style sheet"
        # flask maps this key to blueprint static folder
        endpoint = f'{self.base_path}.static'
        load_src = url_for(endpoint=endpoint, filename=filename)
        load_line = f'<link rel="stylesheet" type="text/css" href="{load_src}" >'
        return Markup(load_line)
