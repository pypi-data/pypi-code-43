from com.fw.base.base_log import logger


class BaseException(Exception):
    def __init__(self, err_msg: str, e: Exception = None):
        self.err_msg = err_msg

        if e is None:
            e = "NULL"

        self.exception = e
        logger.error("【ERROR】:", err_msg, "-- Stack:", e)
