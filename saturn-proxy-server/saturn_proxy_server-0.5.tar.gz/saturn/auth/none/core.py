class Authenticator:
    method = 0

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, **data):
        pass

    async def authenticate(self, data):
        return True
