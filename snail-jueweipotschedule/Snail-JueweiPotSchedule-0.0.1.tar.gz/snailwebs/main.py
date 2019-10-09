#!/usr/bin/python3

from snailwebs import *
from flask import Flask
from flask import current_app
from flask_restful import Api
app = Flask(__name__, static_folder='./../static')
app.config['SECRET_KEY'] = '123456'

# 加载资源
for res in APP_BLUEPRINTS:
    m, b = res.rsplit('.', 1)

    module = __import__(m, fromlist=True)
    blueprint = getattr(module, b)
    prefix = '/' + getattr(blueprint, 'name')

    app.register_blueprint(blueprint, url_prefix=prefix)

# 加载API资源
api = Api(app)
for res in API_RESOURCES:

    m, c = res.rsplit('.', 1)

    module = __import__(m, fromlist=True)
    clazz = getattr(module, c)
    obj = clazz()

    api.add_resource(clazz, obj.api_path())


@app.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('favicon.ico')


@app.route('/')
def index():
    return current_app.send_static_file('index.html')


@app.route('/css/<filename>')
def css(filename):
    return current_app.send_static_file('css/' + filename)


@app.route('/js/<filename>')
def js(filename):
    return current_app.send_static_file('js/' + filename)


@app.route('/img/<filename>')
def imgs(filename):
    return current_app.send_static_file('img/' + filename)


@app.route('/fonts/<filename>')
def fonts(filename):
    return current_app.send_static_file('fonts/' + filename)


if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0', port=PORT)


