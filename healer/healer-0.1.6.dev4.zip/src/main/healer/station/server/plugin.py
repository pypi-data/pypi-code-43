"""
Flask application extensions
"""

from __future__ import annotations

from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended.jwt_manager import JWTManager
from flask_login.login_manager import LoginManager

from healer.station.web_npm.arkon import WebPack

from .support.peewee_plugin import PeeweeDatabaseExt
from .support.transcrypt_plugin import TranscryptResourceExt

cors = CORS()
bcrypt = Bcrypt()
login = LoginManager()
tokenizer = JWTManager()
datawrap = PeeweeDatabaseExt()

web_pack = WebPack('web_pack')
station_client = TranscryptResourceExt('client', 'healer.station.client')

registration_list = [

    cors,
    bcrypt,
    login,
    datawrap,
    tokenizer,

    web_pack,
    station_client,

]
