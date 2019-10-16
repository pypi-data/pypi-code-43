from collections import OrderedDict
from configparser import ConfigParser
from typing import Optional

from nezha.file import File

from .base import AuthenticationBase


class AuthenticationFile(AuthenticationBase):

    def __init__(self, code_book: str = '', section: str = ''):
        """

        :param code_book: records account and password, support ini
        """
        super().__init__()
        self.file_path: str = code_book
        self.file_content: Optional[OrderedDict] = self.read_config(self.file_path)
        self.default_section: str = section

    @staticmethod
    def read_config(file: str) -> Optional[OrderedDict]:
        suffix = File(file).suffix
        if suffix == 'ini':
            conf = ConfigParser()
            conf.read(file, encoding='utf-8')
            return getattr(conf, '_sections', None)
        return None

    def get_password(self, account: str, section: str = None) -> str:
        return self.file_content.get(section or self.default_section, {}).get(account, '') if self.file_content else ''

    def match_password(self, unverified: str, existed: str) -> bool:
        return unverified == existed


if __name__ == '__main__':
    auth = AuthenticationFile('', '')
    passwd = auth.get_password('c')
    print(passwd)
