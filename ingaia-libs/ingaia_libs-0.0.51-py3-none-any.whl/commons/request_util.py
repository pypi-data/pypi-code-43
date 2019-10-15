import json
from flask import request
from werkzeug.exceptions import BadRequest


def get_request_payload():
    if request.data is None or request.data == b'':
        raise BadRequest('The request body is empty')

    payload = json.loads(request.data)

    if payload is None:
        raise BadRequest('The payload is empty')

    return payload
