import re
import math


class Utils:
    @classmethod
    def get_nim_headers(cls, request):
        NIM_HEADER_REG_EXP = r"^HTTP\_NIM\_"
        HTTP_REG_EXP = r"^HTTP\_"
        nim_headers = {}
        for key,value in request.META.items():
            if re.match(NIM_HEADER_REG_EXP, key):
                transformed_key = re.sub(HTTP_REG_EXP, "", key).replace("_", "-")
                nim_headers[transformed_key] = value
        return nim_headers

    @classmethod
    def adjust_string_length(cls, value, max_length):
        TRUNCATE_INDICATOR = "---[TRUNCATED]---"
        output = value
        if max_length and max_length.upper() != "OFF":
            max_length = int(max_length)
            value = str(value)
            length = len(value)
            if length > max_length:
                extra_chars = int(math.floor((length - max_length) / 2))
                middle = int(math.floor(length / 2))
                output = "".join([value[:middle - extra_chars], TRUNCATE_INDICATOR, value[middle + extra_chars:]])
        return output
