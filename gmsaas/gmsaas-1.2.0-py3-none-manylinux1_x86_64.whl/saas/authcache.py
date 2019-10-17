# Copyright 2019 Genymobile
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Genymotion Cloud SaaS auth cache functions
"""

from gmsaas.crypto import cypher, decypher
from gmsaas.storage import get_auth_storage, AUTH_FILENAME

AUTH_EMAIL_KEY = "email"
AUTH_PASSWORD_KEY = "password"
AUTH_JWT_KEY = "jwt"


def get_path():
    """ Return auth cache path """
    return AUTH_FILENAME


def get_email():
    """ Return email from cache or None """
    return get_auth_storage().get(AUTH_EMAIL_KEY)


def get_password():
    """ Return decoded password from cache or None """
    password = get_auth_storage().get(AUTH_PASSWORD_KEY)
    if not password:
        return None
    return decypher(password)


def get_jwt():
    """ Return jwt from cache or None """
    return get_auth_storage().get(AUTH_JWT_KEY)


def set_email(email):
    """ Save email in cache """
    get_auth_storage().put(AUTH_EMAIL_KEY, email)


def set_password(password):
    """ Save encoded password in cache """
    get_auth_storage().put(AUTH_PASSWORD_KEY, cypher(password))


def set_jwt(jwt):
    """ Save jwt and decoded token in cache """
    get_auth_storage().put(AUTH_JWT_KEY, jwt)


def clear():
    """ Clear all cache entries """
    get_auth_storage().remove(AUTH_EMAIL_KEY)
    get_auth_storage().remove(AUTH_PASSWORD_KEY)
    get_auth_storage().remove(AUTH_JWT_KEY)
