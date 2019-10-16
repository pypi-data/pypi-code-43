from pysubway.model.user import User

from .base import AuthenticationBase


class AuthenticationMysql(AuthenticationBase):

    def __init__(self, salt: str = ''):
        super().__init__()
        self.salt = salt

    def get_password(self, account: str, section: str = None) -> str:
        record: User = User.query.filter_by().first()
        return record.password if record else ''

    def match_password(self, unverified: str, existed: str) -> bool:
        return unverified == User.generate_hash_password(existed, self.salt)
