import jwt

from jwt.exceptions import PyJWTError
from werkzeug.exceptions import Unauthorized
from .config import config
from ingaia.gcloud import StorageUtil


def decode_token(token):
    """
    Function responsible for decode the token informed by the client

    :param token:   JWT Token
    :return:        json decoded
    :raise:         Unauthorized when token is invalid
    """
    try:
        public_key = StorageUtil(config.RSA_BUCKET, config.RSA_PUBLIC_KEY, project=config.RSA_PROJECT_REF).get_content()
        return jwt.decode(token, public_key, algorithms=['RS256'])
    except PyJWTError as e:
        raise Unauthorized()
