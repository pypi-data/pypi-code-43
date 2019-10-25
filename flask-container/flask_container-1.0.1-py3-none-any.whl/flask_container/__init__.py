import os
import json
from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flask_container.sqlite'),
    )
    ### swagger specific ###
    SWAGGER_URL = '/docs'
    API_URL = '/static/swagger.json'
    SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "flask_container"
        }
    )
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
    ### end swagger specific ###

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from flask_container import db
    db.init_app(app)
    from flask_container import api, apps
    app.register_blueprint(apps.bp)
    app.register_blueprint(api.bp)

    apps_config_path =  os.path.join(os.path.dirname(os.path.realpath(__file__)),'apps/apps.json')

    def app_loader():
        with open(apps_config_path, 'r') as modules:
            for module in json.load(modules):
                registrar = __import__(module.get('name'), fromlist=['bp'])
                app.register_blueprint(registrar.bp, url_prefix=module.get('path'))

    # app.add_url_rule('/', endpoint='index')

    app_loader()

    return app
