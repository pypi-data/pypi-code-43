
from __future__ import annotations

import math
import os

import pygal
from flask import Blueprint
from flask import abort
from flask import jsonify
from flask import render_template
from flask import request
from flask.helpers import get_root_path
from flask.helpers import send_file
from flask_login import login_required

blueprint = Blueprint('arkon', __name__)


@blueprint.route('/')
def ara_client():
    return render_template('client.html')


@blueprint.route('/chart.svg')
@login_required
def ara_chart():
    chart = pygal.XY()
    chart.title = 'XY Cosinus'
    chart.add('x = cos(y)', [(math.cos(x / 10.), x / 10.) for x in range(-50, 50, 5)])
    chart.add('y = cos(x)', [(x / 10., math.cos(x / 10.)) for x in range(-50, 50, 5)])
    chart.add('x = +1', [(1, -5), (1, 5)])
    chart.add('x = -1', [(-1, -5), (-1, 5)])
    chart.add('y = +1', [(-5, 1), (5, 1)])
    chart.add('y = -1', [(-5, -1), (5, -1)])
    return chart.render_response()


@blueprint.route('/import/<path:code_path>')
def ara_import(code_path:str):
    if code_path.endswith('.js'):
        abort(404)
    elif code_path.endswith('__init__.py'):
        return "", 200
    elif code_path.endswith('.py'):
        import_path = code_path.replace('.py', '')
    else:
        abort(404)
    #
    import_name = import_path.replace('/', '.')
    module_root = get_root_path(import_name)
    code_file = os.path.basename(code_path)
    full_path = f"{module_root}/{code_file}"
    if not os.path.exists(full_path):
        abort(404)
    return send_file(full_path, mimetype="text/python")
