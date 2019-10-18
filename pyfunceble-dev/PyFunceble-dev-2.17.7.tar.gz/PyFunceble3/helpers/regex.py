from re import compile as re_compile
from re import escape as re_escape
from re import sub as re_sub


class Regex:
    def __init__(self, regex, escape=False):
        if escape:
            self.regex = re_escape(self.regex)
        else:
            self.regex = regex

    def get_not_matching_list(self, data):
        pre_result = re_compile(self.regex)

        return [x for x in data if not pre_result.search(str(x))]

    def get_matching_list(self, data):
        pre_result = re_compile(self.regex)

        return [x for x in data if pre_result.search(str(x))]

    def match(self, data, rematch=False, group=0, return_match=True):
        result = []
        to_match = re_compile(self.regex)

        if rematch:
            pre_result = to_match.findall(data)
        else:
            pre_result = to_match.search(data)

        if return_match and pre_result:
            if rematch:
                for res in pre_result:
                    if isinstance(res, tuple):
                        result.extend(list(res))
                    else:
                        result.append(data)

                if group != 0:
                    return result[group]
            else:
                result = pre_result.group(group).strip()

            return result

        if not return_match and pre_result:
            return True
        return False

    def replace_match(self, data, replacement, occurences=0):
        return re_sub(self.regex, replacement, data, occurences)
