"""
"""

from __future__ import annotations

import uuid
from typing import Optional
from typing import Union

from flask import current_app
from flask_login import UserMixin

from healer.config import CONFIG
from healer.persist.support.schemaless import NoSqlIndex
from healer.persist.support.schemaless import NoSqlRecord
from healer.persist.support.schemaless import NoSqlStore
from healer.station.server import plugin
from healer.support.files import FilesSupport
from healer.support.hronos import DateTime
from healer.support.network import NetworkSupport
from healer.support.typing import override


@plugin.login.user_loader
def load_user(guid:str) -> Optional[User]:
    return UserSupport.get_by_guid(guid)


@plugin.tokenizer.token_in_blacklist_loader
def check_blacklist_token(token_entry:dict) -> bool:
    blacklist = current_app.extensions['tokenizer_blacklist']
    jti = token_entry['jti']
    return jti in blacklist


def setup_admin() -> None:
    section = 'station/server/user/admin'
    config = CONFIG[section]
    guid = uuid.UUID(config['guid']).hex
    user = load_user(guid)
    if user:
        pass
    else:
        username = config['username']
        password = config['password']
        mailaddr = config['mailaddr']
        rolelist = CONFIG.get_list(section, 'rolelist')
        UserSupport.ensure_user(guid, username, password, mailaddr, rolelist, True)


class User(UserMixin):

    login_column = "account_login"

    def __init__(self, record:NoSqlRecord):
        self.record = record
        self.login_bundle = self.record.bundle_load(self.login_column)
        if not self.login_bundle['stamp']['created']:
            self.login_bundle['stamp']['created'] = str(DateTime.now())

    @override
    def get_id(self) -> str:
        return self.record.row_id

    @property
    def mailaddr(self) -> str:
        return self.login_bundle['mail_addr']

    @mailaddr.setter
    def mailaddr(self, mailaddr:str) -> None:
        self.login_bundle['mail_addr'] = UserSupport.make_mail(mailaddr)

    @property
    def username(self) -> str:
        return self.login_bundle['user_name']

    @username.setter
    def username(self, username:str) -> None:
        self.login_bundle['user_name'] = UserSupport.make_user(username)

    @property
    def password(self) -> str:
        return self.login_bundle['pass_hash']

    @password.setter
    def password(self, password:str) -> None:
        self.login_bundle['pass_hash'] = UserSupport.make_hash(password)

    @property
    def rolelist(self) -> list[str]:
        return self.login_bundle['role_list']

    @rolelist.setter
    def rolelist(self, rolelist:list[str]) -> None:
        self.login_bundle['role_list'] = UserSupport.make_role(rolelist)

    def delete(self):
        pass  # TODO

    def save(self, default:bool=False):
        self.login_bundle['origin']['machine_id'] = FilesSupport.machine_id()
        self.login_bundle['origin']['host_name'] = NetworkSupport.host_name()
        self.login_bundle['stamp']['updated'] = str(DateTime.now())
        stamp = 1 if default else None
        self.record.bundle_save(self.login_column, stamp)

    def check_password(self, password:str) -> bool:
        pass_hash = bytes.fromhex(self.password)
        return plugin.bcrypt.check_password_hash(pass_hash, password)

    def __str__(self):
        return f"User(guid='{self.get_id()}', username='{self.username}', mailaddr='{self.mailaddr}')"


class UserSupport:

    store_name = "settings"

    @staticmethod
    def store() -> NoSqlStore:
        database = plugin.datawrap.database
        store = database.ensure_store(UserSupport.store_name)
        return store

    @staticmethod
    def make_mail(mailaddr:str) -> str:
        return mailaddr.lower() if mailaddr else ""

    @staticmethod
    def make_user(username:str) -> str:
        return username.lower() if username else ""

    @staticmethod
    def make_role(rolelist:list[str]) -> str:
        return rolelist if rolelist else []

    @staticmethod
    def make_hash(password:str) -> str:
        return plugin.bcrypt.generate_password_hash(password).hex() if password else ""

    @staticmethod
    def ensure_record(guid:str) -> str:
        return UserSupport.store().ensure_record(row_id=guid)

    @staticmethod
    def get_user(guid) -> User:
        record = UserSupport.ensure_record(guid)
        return User(record)

    @staticmethod
    def ensure_user(
            guid:str,
            username:str,
            password:str,
            mailaddr:str,
            rolelist:list[str],
            default:bool=False) -> User:
        user = UserSupport.get_user(guid)
        user.username = username
        user.password = password
        user.mailaddr = mailaddr
        user.rolelist = rolelist
        user.save(default)
        return user

    @staticmethod
    def get_by_guid(guid:str) -> Optional[User]:
        user = UserSupport.get_user(guid)
        if user.username and user.password:
            return user
        else:
            return None

    @staticmethod
    def ensure_index(json_path:str) -> NoSqlIndex:
        store = UserSupport.store()
        nosql_index = store.ensure_index(User.login_column, json_path)
        return nosql_index

    @staticmethod
    def get_by_name(username:str) -> Optional[User]:
        user_name = UserSupport.make_user(username)
        nosql_index = UserSupport.ensure_index("$.user_name")
        return nosql_index.query(user_name).single(User)

    @staticmethod
    def get_by_mail(mailaddr:str) -> Optional[User]:
        mail_addr = UserSupport.make_mail(mailaddr)
        nosql_index = UserSupport.ensure_index("$.mail_addr")
        return nosql_index.query(mail_addr).single(User)
