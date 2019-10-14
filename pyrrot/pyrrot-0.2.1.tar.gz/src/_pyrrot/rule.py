import datetime
import json
from http import HTTPStatus

from flask import jsonify, render_template, request

from .comparison import Comparisons
from .constant import CALL_COUNT_PARAM, CONFIG_PARAM
from .schema import METHODS


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super(JSONEncoder, self).default(obj)


def register_rules(app):
    def _build_template(configurations, output=None):
        response = []
        for config in configurations:
            data = {'id': config['id'],
                    'call_count': app.config[CALL_COUNT_PARAM][config['id']]}
            if not output:
                data['code'] = json.dumps(config, indent=4, sort_keys=True, cls=JSONEncoder)
            response.append(data)
        return response

    def _build_response(value):
        app.config[CALL_COUNT_PARAM][value['id']] += 1
        then_value = value['then']
        then_value['header'] = then_value.get('header', {})
        then_value['header']['call_count'] = app.config[CALL_COUNT_PARAM][value['id']]
        return jsonify(then_value.get('body')), then_value.get('code'), then_value.get('header')

    @app.route('/', methods=METHODS)
    def get_request_without_path():
        output_format = request.args.get('output', '')
        if output_format == 'json':
            return jsonify(_build_template(app.config[CONFIG_PARAM], output_format))
        return render_template('config.html', configurations=_build_template(app.config[CONFIG_PARAM]))

    @app.route('/<path:path>', methods=METHODS)
    def get_request_with_path(path):
        comparison = Comparisons(path)
        selected_config = list(filter(comparison.compare, app.config[CONFIG_PARAM]))
        if selected_config:
            return _build_response(selected_config[0])
        return jsonify(comparison.result), HTTPStatus.NOT_FOUND


def register_exceptions(app):
    @app.errorhandler(Exception)
    def exception(_):
        response = jsonify({'message': 'URL NOT FOUND'})
        response.status_code = HTTPStatus.NOT_FOUND
        return response
