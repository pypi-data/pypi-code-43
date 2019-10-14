import os
import jwt

from jwt.exceptions import PyJWTError
from werkzeug.exceptions import Unauthorized
from ingaia.gcloud import StorageUtil

from ingaia.gcloud import ProjectReference

RSA_PROJECT_ID = 'ingaia-authentication-api'
RSA_BUCKET_LOCATION = ''  # TODO
RSA_BUCKET = 'authentication-rsa'
RSA_PUBLIC_KEY = 'jwt-token-key.pub'
RSA_PROJECT_REF = ProjectReference(RSA_PROJECT_ID, RSA_BUCKET_LOCATION)

public_key = StorageUtil(RSA_BUCKET, RSA_PUBLIC_KEY, project=RSA_PROJECT_REF).get_content()


def decode_token(token):
    """
    Function responsible for decode the token informed by the client

    :param token:   JWT Token
    :return:        json decoded
    :raise:         Unauthorized when token is invalid
    """
    try:
        return jwt.decode(token, public_key, algorithms=['RS256'])
    except PyJWTError as e:
        raise Unauthorized()
