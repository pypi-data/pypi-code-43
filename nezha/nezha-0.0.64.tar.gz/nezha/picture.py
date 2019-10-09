import base64
from collections import namedtuple
from typing import Union, Optional, List

from nezha.ustring import to_bytes, to_str

base64_picture = namedtuple('base64_picture', ['format', 'data_str', 'data_binary'])


class Picture:

    @staticmethod
    def to_base64(s: Union[str, bytes, bytearray], is_file: bool = False) -> str:
        if is_file and isinstance(s, str):
            with open(s, mode='rb') as f:
                content = f.read()
        else:
            content = to_bytes(s)
        return to_str(base64.b64encode(content))

    @staticmethod
    def parse_base64(data: Union[str, bytes, bytearray]) -> Optional[base64_picture]:
        """
        usage: get picture format from picture encoded base64

        :param data: picture encoded base64, sample: "image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAh"
        :return: 'jpg' or 'png'; lower letter
        """

        def valid_split(arr: List) -> bool:
            if len(arr) == 1:
                print(sample)
                return False
            return True

        sample = 'valid parameter like: image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAh'
        s: str = to_str(data)

        split: List = s.split(';')
        if not valid_split(split):
            return

        contained_type, contained_data = split
        split_sec: List = contained_type.split('/')
        if not valid_split(split_sec):
            return

        picture_format = 'jpg' if split_sec[1] == 'jpeg' else split_sec[1]
        split_thd: List = contained_data.split(',')
        if not valid_split(split_thd):
            return

        _, picture_data = split_thd
        try:
            data_binary = base64.b64decode(picture_data)
        except Exception as e:
            print(e)
            data_binary = b''
        return base64_picture(picture_format, picture_data, data_binary)
