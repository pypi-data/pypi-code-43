import os
import jwt

from jwt.exceptions import PyJWTError
from werkzeug.exceptions import Unauthorized

jwt_key_pub_path = f'{os.path.abspath(os.path.dirname(__file__))}/jwt-key.pub'


def decode_token(token):
    """
    Function responsible for decode the token informed by the client

    :param token:   JWT Token
    :return:        json decoded
    :raise:         Unauthorized when token is invalid
    """
    try:
        return jwt.decode(token, open(jwt_key_pub_path).read(), algorithms=['RS256'])
    except PyJWTError as e:
        raise Unauthorized()
