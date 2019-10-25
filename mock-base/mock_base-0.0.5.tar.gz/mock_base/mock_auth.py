from . import MockApp, _DEFAULT_APP_NAME
import json
import base64
from typing import Dict


def verify_id_token(id_token: str, app: MockApp = None, check_revoked=False) -> Dict:
    bb: bytes = base64.decodebytes(id_token.encode())
    jj: Dict = json.loads(bb.decode())
    if app is not None:
        assert jj.get("app") == app.name
    else:
        assert jj.get("app") == _DEFAULT_APP_NAME
    return jj


def get_user(uid, app=None):
    pass