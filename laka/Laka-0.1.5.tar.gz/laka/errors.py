
class ValidateError(Exception):
    """
    参数验证失败
    """
    def __init__(self, message="validate params failed"):
        Exception.__init__(self, message)


class HandlerNotFound(Exception):
    """
    未找到 handler
    """
    def __init__(self, message="handler not found"):
        Exception.__init__(self, message)


class MakeHandlerResponseError(Exception):
    """
    handler 返回的数据不合法
    """
    def __init__(self, message="response type error"):
        Exception.__init__(self, message)


class InvalidHandler(Exception):
    """
    非法的 handler，handler 必须继承于 Handler 类
    """
    def __init__(self, message="invalid handler"):
        Exception.__init__(self, message)


class MakeCommandError(Exception):
    """
    创建 Command 失败
    """
    def __init__(self, message="failed to init command"):
        Exception.__init__(self, message)


class InvalidMessage(Exception):
    """
    未能识别的消息，消息必须能转化成 Command
    """
    def __init__(self, message="invalid message"):
        Exception.__init__(self, message)


class MakeResponseError(Exception):
    """
    创建 Response 失败
    """
    def __init__(self, message="make response error"):
        Exception.__init__(self, message)


class MakeRequestError(Exception):
    """
    创建 Request 失败
    """
    def __init__(self, message="make response error"):
        Exception.__init__(self, message)
