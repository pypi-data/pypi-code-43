from enum import Enum, unique
import logging
from etornado.singleton import SingletonMeta

HTTP_OK = 200

@unique
class ErrorCode(Enum):
    NONE = 0
    UNKNOWN = 100
    UNSUPPORTED_URL = 101
    UNSUPPORTED_METHOD = 102


ERROR_INFO_MAP = {
    ErrorCode.NONE: "ok",
    ErrorCode.UNKNOWN: "unknown error",
    ErrorCode.UNSUPPORTED_URL: "unsupported url [{url}]",
    ErrorCode.UNSUPPORTED_METHOD:
    "unsupported method [{method}] for url [{url}]",
}


class ErrorCodeManager(object, metaclass=SingletonMeta):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.error_infos = {}
        self.register_error_enum(ErrorCode, ERROR_INFO_MAP)

    def register_error_enum(self, error_enum, error_info_map):
        for name, member in error_enum.__members__.items():
            error_msg = error_info_map.get(member, "")
            if not error_msg:
                self.logger.warn("error msg of [%s] is empty", member)
            self.register_error_code(member.value, error_msg)

    def register_error_code(self, error_num, error_msg):
        if error_num in self.error_infos:
            self.logger.error("error_num [%d] has be registered"
                    " with message[%s]", error_num, error_msg)
            return False
        self.error_infos[error_num] = error_msg

    def format_error_info(self, error_code, **kwargs):
        if error_code is None:
            error_code = ErrorCode.UNKNOWN
        if isinstance(error_code, Enum):
            error_code = error_code.value
        error_message = self.error_infos.get(error_code, "").format(**kwargs)
        return {"error_code": error_code, "error_message": error_message}


error_code_manager = ErrorCodeManager()
