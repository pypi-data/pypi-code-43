from typing import Optional, Dict

from pymongo import MongoClient

from .base import AuthenticationBase


class AuthenticationMongo(AuthenticationBase):

    def __init__(self,
                 client: Optional[MongoClient] = None,
                 db_name: str = '',
                 collection: str = '',
                 key_account: str = 'account_name',
                 salt: str = ''):
        super().__init__()
        self.salt = salt
        if not client:
            raise ValueError(f'client {client} not exist')
        self.client = client
        self.db = db_name
        self.collection = collection
        self.key_account = key_account

    def get_password(self, account: str, key_password: str = 'password') -> str:
        record: Dict = self.client[self.db][self.collection].find_one({self.key_account: account})
        return record[key_password] if record else ''

    def generate_hash_password(self, existed, salt):
        return existed

    def match_password(self, unverified: str, existed: str) -> bool:
        return unverified == self.generate_hash_password(existed, self.salt)
