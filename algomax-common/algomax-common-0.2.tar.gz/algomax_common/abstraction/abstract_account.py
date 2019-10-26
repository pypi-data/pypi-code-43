from abc import ABC, abstractmethod


class AbstractAccount(ABC):
    @abstractmethod
    def sign_in_with_token(self):
        pass

    @abstractmethod
    def sign_in_with_username_and_password(self, data: dict):
        pass

    @abstractmethod
    def sign_in_from_config_file(self):
        pass

    @abstractmethod
    def delete_session(self, access_token: str):
        pass

    @abstractmethod
    def get_session_list(self, query: str = None):
        pass

    @abstractmethod
    def get_portfolio(self, query: str = None):
        pass

    @abstractmethod
    def get_balance(self, query: str = None):
        pass

    @abstractmethod
    def get_transactions(self, query: str = None):
        pass

    @abstractmethod
    def delete_all_session(self, account_id: str, type_id: str):
        pass