import fcntl
import functools
import io
import os
import tempfile
import zipfile
from collections import OrderedDict
from configparser import ConfigParser
from typing import TextIO, Union, Tuple, Iterator, List, Callable, Any

import chardet
from chardet.gb2312prober import GB2312Prober
from chardet.latin1prober import Latin1Prober
from nezha.ustring import replace_chinese_comma


def file_dirname(file: str) -> str:
    return os.path.split(file)[0]


def join_path(dirname: str, *path: str) -> str:
    return os.path.join(dirname, *path)


def only_support_str(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrap(self: Any, *args: Any, **kwargs: Any) -> Any:
        if not isinstance(self.file, str):
            raise TypeError(f'only support when self.file {self.file} type is str')
        return func(self, *args, **kwargs)

    return wrap


class File:
    file_dirname = staticmethod(file_dirname)
    join_path = staticmethod(join_path)

    gdk_compatibility = [
        # ascii
        Latin1Prober().charset_name,
        # gbk
        GB2312Prober().charset_name,
        'ISO-8859-9',
    ]

    def __init__(self, file: Union[str, TextIO]):
        self.file: Union[str, TextIO] = file
        self._full_dirname: str = ''
        self._abs_path: str = ''
        # self.filename = self.pure_name + '.' + self.suffix
        self.dirname, self.filename = os.path.split(self.file) if isinstance(self.file, str) else ('', '')
        self.pure_name, self.suffix = self.get_pure_name_and_suffix(self.filename)
        self._encoding: str = ''
        self.__sub_files: List[str] = []

    @staticmethod
    def delete(file: str) -> None:
        if os.path.exists(file):
            os.remove(file)

    @staticmethod
    def get_pure_name_and_suffix(filename: str) -> Tuple[str, str]:
        split = filename.split('.')
        if len(split) == 1:
            split.append('')
        return split[0], split[-1]

    # type ignore is useful, don't delete it.
    @property  # type: ignore
    @only_support_str
    def abs_dirname(self) -> str:
        if not self._full_dirname:
            self._full_dirname = self.this_dir(self.file)  # type: ignore
        return self._full_dirname

    @property  # type: ignore
    @only_support_str
    def abs_path(self) -> str:
        if not self._abs_path:
            self._abs_path = self.join_path(self.abs_dirname, self.pure_name)
        return self._abs_path

    @property  # type: ignore
    @only_support_str
    def encoding(self) -> str:
        """
        {'encoding': 'ascii', 'confidence': 1.0, 'language': ''}
        :param self:
        :return:
        """
        if not self._encoding:
            with open(self.file, mode='rb') as f:  # type: ignore
                # must read all, or the detect result is imprecision
                encoding = chardet.detect(f.read())
                self._encoding = 'gbk' if encoding in self.gdk_compatibility else 'utf-8'
        return self._encoding

    def remove_chinese_comma(self, output: str = 'io') -> Union[str, TextIO, io.StringIO]:
        f: TextIO = io.StringIO()
        try:
            # if not str, treat self.file as TextIO
            f = open(self.file) if isinstance(self.file, str) else self.file
            s = replace_chinese_comma(f.read())
            if output != 'io':
                temp = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding=self.encoding)
                temp.write(s)
                temp.close()
                return temp.name
            else:
                temp = io.StringIO()
                temp.write(s)
                temp.seek(0)
                return temp
        finally:
            f.close()

    @staticmethod
    def this_dir(path: str) -> str:
        """
        return current file dirname
        you can call this method like this_dir(__file__)
        :return: str
        """
        return os.path.dirname(os.path.abspath(path))

    @only_support_str
    def sub_files_first(self) -> Union[Iterator[str], str]:
        """
        if self.file is file and not dir, return self.file
        if self.file is dir, return first sub files
        :return:
        """
        if not os.path.isdir(self.file):  # type: ignore
            return self.abs_path
        return (os.path.join(self.abs_path, sub_name)
                for sub_name in os.listdir(self.file))  # type: ignore

    def _sub_files_all(self, folder: str) -> None:
        """
        find recursively the self.
        :return:
        """
        if os.path.isdir(folder):
            sub_files = File(folder).sub_files_first()
            for i in sub_files:
                self._sub_files_all(i)
        else:
            self.__sub_files.append(folder)

    @property  # type: ignore
    @only_support_str
    def sub_files_all(self) -> Tuple[str, ...]:
        """
        find all sub files in the folder.
        :param folder:
        :return:
        """
        if not self.__sub_files:
            self._sub_files_all(self.file)  # type: ignore
        return tuple(self.__sub_files)


class Open(File):
    """
    example:
    >>>with File(__file__) as f:
    >>> for i in range(10):
    >>>     print(f.readline())
    """

    def __init__(self, file: Union[str, TextIO]):
        super().__init__(file)
        self.f = self.file if isinstance(self.file, (io.StringIO, TextIO)) else open(self.file, encoding=self.encoding)

    def __enter__(self) -> TextIO:
        return self.f

    def __exit__(self, exc_type: str, exc_val: str, exc_tb: str) -> None:
        self.f.close()


class FileIni:

    def __init__(self, file: str):
        super().__init__()
        self.file: str = file
        self.__sections: OrderedDict = OrderedDict()
        self._content: ConfigParser = ConfigParser()

    @property
    def sections(self) -> OrderedDict:
        if not self.__sections:
            conf = ConfigParser()
            conf.read(self.file, encoding='utf-8')
            self.__sections = getattr(conf, '_sections', None)
        return self.__sections

    @property
    def content(self) -> ConfigParser:
        if not self._content.sections():
            conf = ConfigParser()
            conf.read(self.file, encoding='utf-8')
            self._content = conf
        return self._content

    def get_option(self, section: str, option: str, default: str = '') -> str:
        return self.content.get(section, option, fallback=default)

    def get_boolean(self, section: str, option: str, default: bool = False) -> bool:
        return self.content.getboolean(section, option, fallback=default)

    def is_true(self, section: str, option: str) -> bool:
        return self.get_boolean(section, option, False) is True

    def get_val(self,
                section: str,
                option: str,
                default: Union[str, bool] = '',
                val_type: str = '') -> Union[str, bool]:
        if not val_type and isinstance(default, str):
            return self.get_option(section, option, default=default)
        elif val_type == 'bool' and isinstance(default, bool):
            return self.get_boolean(section, option, default=default)
        else:
            raise NotImplementedError()

    def items(self, section: str) -> List[Tuple[str, str]]:
        return self.content.items(section)

    def set(self, section: str, option: str, value: Union[str, bool], lock: bool = True) -> None:
        self.content.set(section, option, str(value))
        with open(self.file, encoding='utf-8') as f:
            if lock:
                fcntl.flock(f, fcntl.LOCK_EX)
            self.content.write(f)


class Dir:

    def __init__(self, dirname: str):
        self.dirname = dirname

    def generate_zip_name(self) -> str:
        return self.dirname.rstrip('/') + '.zip'

    def zip(self) -> str:
        output = self.generate_zip_name()
        zipf = zipfile.ZipFile(output, mode='w')
        pre_len = len(os.path.dirname(self.dirname))
        for parent, dirnames, filenames in os.walk(self.dirname):
            for filename in filenames:
                pathfile = os.path.join(parent, filename)
                arcname = pathfile[pre_len:].strip(os.path.sep)  # 相对路径
                zipf.write(pathfile, arcname)
        zipf.close()
        return output

    def is_dir(self) -> bool:
        return os.path.isdir(self.dirname)

    def mkdir(self) -> None:
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)


if __name__ == '__main__':
    d = Dir('/Users/yutou/shouxin/sxProject/pysubway/pysubway/is_result')
    d.zip()
