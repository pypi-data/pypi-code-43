from typing import Any


class AuthenticationBase:
    """
    verify account and password, the class provided interface
    """

    def __init__(self, **kwargs: Any):
        pass

    def get_password(self, account: str) -> str:
        raise NotImplementedError()

    def match_password(self, unverified: str, existed: str) -> bool:
        raise NotImplementedError()

    def is_authenticated(self, account: str, password: str) -> bool:
        existed = self.get_password(account)
        return self.match_password(password, existed)

    def generate_hash_password(self, existed, salt):
        raise NotImplementedError()
