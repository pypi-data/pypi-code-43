from flask import Blueprint, jsonify, request
from flask_security.decorators import login_required, roles_required

from .database import db
from .models import Challenge, User, Solve

blueprint = Blueprint('challenges_admin', __name__, url_prefix='/api/admin')


@blueprint.route('/challenges')
@roles_required('admin')
@login_required
def get_challenges():
    challenges = Challenge.query.all()
    return jsonify([challenge.serialize() for challenge in challenges])


@blueprint.route('/challenges', methods=['POST'])
@roles_required('admin')
@login_required
def create_challenge():
    challenge = Challenge(
        title=request.json['title'],
        category=request.json['category'],
        body=request.json['body'],
        hint=request.json['hint'],
        solution=request.json['solution'],
        solves=[Solve(
            hinted=False,
            solved=False,
            user=user)
            for user in User.query.all()]
    )
    db.session.add(challenge)
    db.session.commit()
    return jsonify(challenge.serialize())


@blueprint.route('/challenges/<int:challenge_id>', methods=['POST'])
@roles_required('admin')
@login_required
def update_challenge(challenge_id):
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if 'title' in request.json:
        challenge.title = request.json['title']
    if 'category' in request.json:
        challenge.category = request.json['category']
    if 'body' in request.json:
        challenge.body = request.json['body']
    if 'hint' in request.json:
        challenge.hint = request.json['hint']
    if 'solution' in request.json:
        challenge.solution = request.json['solution']
    db.session.commit()
    return jsonify(challenge.serialize())


@blueprint.route('/challenges/<int:challenge_id>', methods=['DELETE'])
@roles_required('admin')
@login_required
def delete_challenge(challenge_id):
    print("Solves", Solve.query.all())
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    db.session.delete(challenge)
    db.session.commit()
    print("Solves", Solve.query.all())
    return ('', 200)


def init_app(app):
    app.register_blueprint(blueprint)
