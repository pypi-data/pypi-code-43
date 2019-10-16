from typing import Any

from .auth_mongo import AuthenticationMongo
from .auth_mysql import AuthenticationMysql
from .base import AuthenticationBase
from .file import AuthenticationFile


class AuthenticationFactory:
    """
    file: should configure code book file;
    db:
    Ensure sqlalchemy should be callable when you call the class AuthenticationDB.
    And table block/role/role_permission/user should existed in database.
    """

    def __new__(self, style: str) -> Any:
        formatted = style.lower()
        if formatted == 'file':
            return AuthenticationFile
        elif formatted == 'mysql':
            return AuthenticationMysql
        elif formatted == 'mongodb':
            return AuthenticationMongo
        raise NotImplementedError(f'the style {style} is not supported now.')
