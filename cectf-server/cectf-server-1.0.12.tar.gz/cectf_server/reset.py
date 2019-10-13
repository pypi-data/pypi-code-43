from flask import Blueprint, current_app
from . import commands

blueprint = Blueprint('reset', __name__, url_prefix='/api')


@blueprint.route('/test/reset', methods=['GET'])
def reset():
    print("Production:", current_app.config['CECTF_PRODUCTION'])
    if not current_app.config['CECTF_PRODUCTION']:
        commands.reset_db()
        commands.populate_test_data()
        print("Done")
        return ('', 200)
    else:
        print("Not resetting the database")
        return ('', 400)


def init_app(app):
    app.register_blueprint(blueprint)
