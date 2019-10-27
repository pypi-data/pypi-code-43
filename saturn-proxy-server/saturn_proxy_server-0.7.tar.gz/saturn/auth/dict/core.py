import logging

class Authenticator:
    method = 2

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, **data):
        self.users = data

    async def authenticate(self, data):
        try:
            login = data[2:2 + data[1]]  # index 1 specifies length of login
            password = data[3 + data[1]:3 + data[1] + data[2 + data[1]]]  # index 2+data[1] specifies length of password
        except IndexError:
            logging.error(f'INDEX ERROR in {self.__class__}. Data: {data} ')
            return False
        if self.users.get(login.decode()) == password.decode():
            return True
        return False
