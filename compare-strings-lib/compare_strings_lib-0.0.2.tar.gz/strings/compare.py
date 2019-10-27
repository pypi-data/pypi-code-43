class InvalidValues(Exception):
    pass


def compare(str1, str2):
    '''compare strings.

    params:
    str1 -- string version 1
    str2 -- string version 2
    the strings are a dot seperated integers.

    return:
    1 if str1 = str2
    0 if str1 > str1
    -1 if str1 < str2

    raise invalidValues exception if non integers value provided
    '''
    try:
        str_v1 = float(''.join(str1.split('.')).replace(' ', ''))
        str_v2 = float(''.join(str2.split('.')).replace(' ', ''))
        if str_v2 == str_v1 and len(str1) == len(str2):
            return 1
        elif str_v1 > str_v2 or len(str1) > len(str2):
            return 0
        else:
            return -1
    except Exception:
        raise InvalidValues(
            f'invalid params. can not compare {str1} to {str2}')
