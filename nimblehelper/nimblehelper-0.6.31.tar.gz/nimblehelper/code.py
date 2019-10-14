from .settings import SUCCESSFUL, INTERNAL_SERVER_ERROR, CODE_LIST
import hashlib


class NimbleCodes:
    @classmethod
    def http_code_helper(cls, code, message=None, data=None):  # pragma: no
        if code not in CODE_LIST:
            code = 500
        response_code_list = {
            200: cls.__200_success(code=code, data=data),
            201: cls.__200_success(code=code, data=data),
            400: cls.__400_error_message(code=code, message=message),
            401: cls.__400_error_message(code=code, message=message),
            403: cls.__400_error_message(code=code, message=message),
            500: cls.__500_error_message(code=code, data=data, message=message)
        }
        return response_code_list[code]

    @staticmethod
    def sha224(data):
        return hashlib.sha224(data.encode("utf-8")).hexdigest()

    @staticmethod
    def __200_success(code, data, message=SUCCESSFUL):  # pragma: no cover
        data = [] if data is None else data
        return {"status": code, "message": message, "data": data}

    @staticmethod
    def __400_error_message(code, message):  # pragma: no cover
        return {"status": code, "message": message, "data": []}

    @staticmethod
    def __500_error_message(code, data, message=INTERNAL_SERVER_ERROR):  # pragma: no cover
        data = [] if data is None else data
        return {"status": code, "message": message, "data": data}