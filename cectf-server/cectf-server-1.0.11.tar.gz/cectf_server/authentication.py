from flask import Blueprint, jsonify
from flask_login import current_user
from flask_security.utils import logout_user
from flask_wtf.csrf import generate_csrf

blueprint = Blueprint('authentication', __name__, url_prefix='/api')


# @app_jwt_required
@blueprint.route('/csrf', methods=['GET'])
def csrf():
    return jsonify({'csrf_token': generate_csrf()})


@blueprint.route('/logout', methods=['GET'])
def logout():
    if current_user.is_authenticated:
        logout_user()
    return ('', 204)


def init_app(app):
    app.register_blueprint(blueprint)
