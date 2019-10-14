import logging
from laka import Laka
from param import Param
from response import Response



# 返回码定义
SUCCESS = 0                 # 成功
COMMAND_NOT_FOUND = 1       # 未找到命令
INVALID_PARAM = 10          # 参数错误

# 返回码对应的提示信息
RESPONSE_MESSAGE = {
    SUCCESS: "",
    COMMAND_NOT_FOUND: "Command not found.",
    INVALID_PARAM: "Invalid params",
}


class CreateUserParam(Param):
    CommandCode = 101
    
    def __init__(self):
        self.account = None
        self.username = None
    
    def validate(self):
        return True

    @classmethod
    def handler(cls, cmd):
        try:
            param = cls.load_from_cmd(cmd)
        except Exception as e:
            logging.error(e)
            return None, INVALID_PARAM
        user = {"username":param.username, "account":param.account}
        return user, SUCCESS
    

if __name__ == "__main__":
    laka = Laka(redis_host="localhost", redis_port=6379, redis_queue="laka_request", response_message=RESPONSE_MESSAGE)
    for cmd in laka.accept_request():
        data, resp_code = None, COMMAND_NOT_FOUND
        if cmd.code == CreateUserParam.CommandCode:
            data, resp_code = CreateUserParam.handler(cmd)
        laka.response(cmd.request_id, resp_code, data)

    