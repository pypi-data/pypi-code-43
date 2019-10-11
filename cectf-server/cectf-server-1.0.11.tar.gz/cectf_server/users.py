from flask import Blueprint, jsonify
from flask_security.core import current_user
from flask_security.decorators import login_required, roles_required

from .models import User


def get_user_by_id(id):
    return User.query.filter_by(id=id).first()


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


blueprint = Blueprint('users', __name__, url_prefix='/api')


@blueprint.route('/user')
@login_required
def get_current_user_route():
    return jsonify(current_user.serialize)


@blueprint.route('/user/username/<string:username>')
@roles_required('admin')
@login_required
def get_user_by_username_route(username):
    user = get_user_by_username(username)
    if user:
        return jsonify(user.serialize)
    return 'Username not found', 404


@blueprint.route('/user/<int:id>')
@roles_required('admin')
@login_required
def get_user_by_id_route(id):
    user = get_user_by_id(id)
    if user:
        return jsonify(user.serialize)
    return 'User ID not found', 404


def init_app(app):
    app.register_blueprint(blueprint)
