from flask import Blueprint, jsonify, request
from flask_security.core import current_user
from flask_security.decorators import login_required, roles_required

from .database import db
from .models import Solve

blueprint = Blueprint('challenges', __name__, url_prefix='/api/ctf')


@blueprint.route('/challenges')
@roles_required('contestant')
@login_required
def get_challenges():
    return jsonify([solve.challenge.serialize(solve=solve) for solve in current_user.solves])


INCORRECT = 0
CORRECT = 1
ALREADY_SOLVED = 2


@blueprint.route('/challenges/<int:challenge_id>', methods=['GET', 'POST'])
@roles_required('contestant')
@login_required
def submit_flag(challenge_id):
    solve = Solve.query.filter_by(
        user_id=current_user.id, challenge_id=challenge_id).first()
    if (request.method == 'GET'):
        return jsonify(solve.challenge.serialize(solve))
    if solve.solved:
        return jsonify({'status': ALREADY_SOLVED})
    flag = request.get_json()['flag']
    print('Submitting flag %s', flag)
    if solve.challenge.solution == flag:
        solve.solved = True
        db.session.commit()
        return jsonify({'status': CORRECT, 'challenge': solve.challenge.serialize(solve)})
    else:
        print('it no match :(')
        return jsonify({'status': INCORRECT})


def init_app(app):
    app.register_blueprint(blueprint)
