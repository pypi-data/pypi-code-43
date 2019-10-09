class IncomingDataError(Exception):
    """
    入参错误
    """
    pass

class RequestFailed(Exception):
    """
    请求失败
    """
    pass


class AuthenticationFailed(Exception):
    """
    鉴权失败
    """
    pass


class EncryptError(Exception):
    """
    加密失败
    """
    pass
