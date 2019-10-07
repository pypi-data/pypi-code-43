"""
"""

from __future__ import annotations

import uuid

from flask import Blueprint
from flask import current_app
from flask import flash
from flask import g
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_raw_jwt
from flask_jwt_extended import jwt_refresh_token_required
from flask_jwt_extended import jwt_required
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from werkzeug.urls import url_parse

from healer.station.server.support.arkon import validate_guid
from healer.station.server.support.arkon import validate_json

from .model import UserSupport

blueprint = Blueprint('user', __name__)

schema_login = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
        'password': {'type': 'string'},
    },
    'required': ['username', 'password'],
}

schema_register = {
    'type': 'object',
    'properties': {
        'mailaddr': {'type': 'string'},
        'username': {'type': 'string'},
        'password1': {'type': 'string'},
        'password2': {'type': 'string'},
    },
    'required': ['mailaddr', 'username', 'password1', 'password2'],
}

schema_update = {
    'type': 'object',
    'properties': {
        'mailaddr': {'type': 'string'},
        'username': {'type': 'string'},
        'password1': {'type':  [ "string", "null" ] },
        'password2': {'type':  [ "string", "null" ] },
        'original_username': {'type': 'string'},
        'original_password': {'type': 'string'},
    },
    'required': ['mailaddr', 'username', 'original_username', 'original_password'],
}


@blueprint.route('/auth/login', methods=['POST'])
@validate_guid(False)
@validate_json(schema_login)
def ara_auth_login():
    username = g.data['username']
    password = g.data['password']
    user = UserSupport.get_by_name(username)
    if user and user.check_password(password):
        user_guid = user.get_id()
        user_name = user.username
        user_mail = user.mailaddr
        user_role = user.rolelist
        access_token = create_access_token(identity=user_guid)
        refresh_token = create_refresh_token(identity=user_guid)
        return jsonify(
            user_guid=user_guid,
            user_name=user_name,
            user_mail=user_mail,
            user_role=user_role,
            access_token=access_token,
            refresh_token=refresh_token,
        ), 200
    else:
        return jsonify(message="need login"), 401


@blueprint.route('/auth/logout', methods=['POST'])
@jwt_required
def ara_auth_logout():
    blacklist = current_app.extensions['tokenizer_blacklist']
    token_entry:dict = get_raw_jwt()
    jti = token_entry['jti']
    blacklist.add(jti)
    return jsonify(
        message='logout ok',
    ), 200


@blueprint.route('/auth/register', methods=['POST'])
@validate_guid(False)
@validate_json(schema_register)
def ara_auth_register():
    mailaddr = g.data['mailaddr']
    username = g.data['username']
    password1 = g.data['password1']
    password2 = g.data['password2']
    if password1 == password2:
        password = password1
    else:
        return jsonify(message="need password match"), 400
    user = UserSupport.get_by_name(username)
    if user:
        return jsonify(message="need unique user"), 400
    guid = uuid.uuid4().hex
    rolelist = []
    user = UserSupport.ensure_user(guid, username, password, mailaddr, rolelist)
    return jsonify(
        user_guid=guid,
    ), 200


@blueprint.route('/auth/update', methods=['POST'])
@jwt_required
@validate_guid(True)
@validate_json(schema_update)
def ara_auth_update():
    user_guid = g.guid
    mailaddr = g.data['mailaddr']
    username = g.data['username']
    password1 = g.data['password1']
    password2 = g.data['password2']
    original_username = g.data['original_username']
    original_password = g.data['original_password']

    has_pass_change = password1 and password2
    if has_pass_change and (password1 != password2):
        return jsonify(message="need password match"), 400

    if username != original_username:
        user = UserSupport.get_by_name(username)
        if user:
            return jsonify(message="need unique user"), 400

    user = UserSupport.get_by_guid(user_guid)
    if not user:
        return jsonify(message="need proper user"), 400

    has_user = user.username == original_username
    has_pass = user.check_password(original_password)
    has_login = has_user and has_pass
    if not has_login:
        return jsonify(message="need proper login"), 400

    user.mailaddr = mailaddr
    user.username = username
    if has_pass_change:
        user.password = password1
    user.save()
    user_name = user.username
    user_mail = user.mailaddr
    user_role = user.rolelist
    access_token = create_access_token(identity=user_guid)
    return jsonify(
        user_guid=user_guid,
        user_name=user_name,
        user_mail=user_mail,
        user_role=user_role,
        access_token=access_token,
    ), 200


@blueprint.route('/auth/refresh', methods=['POST'])
@validate_guid(True)
@jwt_refresh_token_required
def ara_auth_refresh():
    user_guid = g.guid
    return jsonify(
        access_token=create_access_token(identity=user_guid)
    ), 200
