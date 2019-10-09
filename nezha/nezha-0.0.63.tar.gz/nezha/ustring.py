import re
import secrets
import uuid
from typing import Union, List, Tuple, Optional

PATTERN_CHINESE_NAME = re.compile(r'[^\u4e00-\u9fa5·]+')


def remove_invisible(s: str) -> str:
    """
    support remove \t \n \xa0 ...
    :param s:
    :return:
    """
    return ''.join(s.split())


def unique_id() -> str:
    return str(uuid.uuid1())


def to_bytes(s: Union[str, bytes]) -> bytes:
    if isinstance(s, (bytes, bytearray)):
        return s
    return s.encode('utf-8')


def to_str(b: Union[bytes, str]) -> str:
    if isinstance(b, str):
        return b
    return b.decode('utf-8')


def random_key(length: int) -> str:
    if not isinstance(length, int):
        raise Exception(f'nbytes {length} type {type(length)} not int')
    return secrets.token_hex(nbytes=length)[0:length]


def camelize2underline(camelize_words: str, separator: str = "_") -> str:
    u"""
    驼峰转下划线的方法；
    :param camelize_words: 需要转化的字符串
    :param separator: _
    :return: 字符串
    """
    sep = separator + r'\1'
    if not camelize_words:
        return ""
    if not isinstance(camelize_words, str):
        raise ValueError('camelize_words {} must be str'.format(camelize_words))
    pattern = re.compile(r'([A-Z]{1})')
    sub = re.sub(pattern, sep, camelize_words).lower()
    return sub


def is_chinese_name(value: str) -> bool:
    u"""
    校验姓名是否是由汉字或汉字和·组成（王大锤 or 买买提·古力娜扎·迪丽热巴）
    :param value: name type is str
    :return:bool  符合格式的name返回 True 否则返回False
    """
    if not isinstance(value, str):
        raise ValueError("value {} type must be string".format(value))
    return PATTERN_CHINESE_NAME.match(value) is not None


def clean_str(s: str, striped: Union[List[str], str, None] = None) -> str:
    """

    :param s:
    :param striped: need strip character.
    :return:
    """
    s = str(s)
    striped = striped or []
    striped = striped if isinstance(striped, list) else [striped, ]
    for chars in striped:
        s = s.strip(chars)
    return ''.join(s.split())


def replace_chinese_comma(s: str) -> str:
    chinese_comma = '，'
    english_comma = ','
    return s.replace(chinese_comma, english_comma)


def is_invalid_str(*s: str,
                   invalid_str: Tuple[str, ...] = ('', '\n', '\t'),
                   invalid_length: Tuple[int, ...] = (0, 1)
                   ) -> bool:
    rules = (
        lambda *x: set(i in invalid_str for i in x) != {False},
        # debug: i or '' is used for i is None.
        lambda *x: set(len(i or '') in invalid_length for i in x) != {False},
    )
    for hit_rule in rules:
        if hit_rule(*s):
            return True
    return False


def isascii(data):
    try:
        # add in python3.7
        return data.isascii()
    except Exception as e:
        try:
            data.encode('ascii')
            return True
        except UnicodeEncodeError as e:
            return False


def is_valid_password(data: str, length_range: Optional[List[int]] = None) -> bool:
    length_range = length_range or tuple(range(8, 33))
    if not (isinstance(data, str) and len(data) in length_range):
        return False
    return isascii(data)


if __name__ == '__main__':
    s = is_invalid_str('s2')
    print(s)
