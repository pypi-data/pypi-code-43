from typing import Tuple, Any, Dict

from flask_requests import get_data, ParameterError
from flask_simple_token import FlaskToken
from flask_simple_user import FlaskUser


class AccessDeny(Exception):
    pass


def attrs(obj) -> Tuple[Tuple[str, Any], ...]:
    condition = lambda item: not (item[0].startswith('__') or isinstance(item[1], (classmethod, staticmethod)))
    return tuple(filter(condition, obj.__dict__.items()))


class FlaskLogin:
    """
    Flask login view
    using sqlalchemy as backend db and store cache in redis.
    """

    def __init__(self, user_ins: FlaskUser,
                 cache_obj,
                 user_ins_unique_filed: str,
                 token_key: str,
                 token_secrete_key: str,
                 account_key: str = 'account', password_key: str = 'password'):
        self.account_key = account_key
        self.password_key = password_key
        self.token_key = token_key
        self.token_secrete_key = token_secrete_key
        self.user_ins: FlaskUser = user_ins
        self.cache_obj = cache_obj
        self.user_ins_unique_filed = user_ins_unique_filed
        self.user_ins_unique_val = getattr(self.user_ins, self.user_ins_unique_filed, None)
        self.retry_times_key = f'retry_times_key_{self.user_ins_unique_val}'
        self.token_ins: FlaskToken = FlaskToken(self.token_key, self.token_secrete_key, cache=self.cache_obj)

    def get_account_and_password(self) -> Tuple:
        """
        get account and password from http request.
        :param account_key:
        :param password_key:
        :return:
        """
        received_data = get_data(self.account_key, self.password_key)
        if not received_data:
            raise ParameterError(
                f'parse data from request failed. received_data {received_data}, account_key {self.account_key} password_key {self.password_key}')
        return received_data

    def add_retry_times(self, expire: int = 3600) -> int:
        """
        :param account: login account, it should be unique key.
        :param expire: unit second. cache expire time.
        :return:
        """
        retried_times = int(self.cache_obj.get(self.retry_times_key) or 0)
        current_retry_times = retried_times + 1
        self.cache_obj.set(self.retry_times_key, current_retry_times + 1, expire)
        return current_retry_times

    def get_retry_times(self) -> int:
        return int(self.cache_obj.get(self.retry_times_key) or 0)

    def is_beyond_retry_times(self, max_retry_times: int) -> bool:
        return self.get_retry_times() > max_retry_times

    def check_account(self, account: str, password: str) -> FlaskUser:
        account_ins = FlaskUser.filter_one({self.user_ins_unique_filed: account})
        self.user_ins.login(account_ins, password)
        return account_ins

    def check_retry_times(self, max_retry_times: int, expire: int = 3600):
        if self.is_beyond_retry_times(max_retry_times):
            raise AccessDeny(f'the retry_times of login failed is beyond {max_retry_times}')
        self.add_retry_times(expire=expire)

    def login(self, max_retry_times: int, retry_times_expire: int = 3600, token_expire: int = 3600 * 24) -> Dict:
        account, password = self.get_account_and_password()
        # retry_times
        self.check_retry_times(max_retry_times, expire=retry_times_expire)
        # verify account.
        account_ins = self.check_account(account, password)
        # generate token.
        token = self.token_ins.generate({self.account_key: account}, token_expire)
        # first login
        is_first_login = self.user_ins.is_first_login(account_ins)
        account_ins.login(account_ins, password)
        result = dict(attrs(account_ins))
        result.update(dict(
            token=token,
            is_first_login=is_first_login
        ))
        return result
