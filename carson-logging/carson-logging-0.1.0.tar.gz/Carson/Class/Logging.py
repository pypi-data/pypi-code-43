from dataclasses import dataclass, InitVar
import logging
from os import path, makedirs


@dataclass(repr=False, eq=False)
class _CLoggingBase:
    __slots__ = ['_log_name', '_log_path',
                 '_log', '_file_handler', '_stream_handler'  # hidden member (that mean it will implement by member
                 ]
    _log_name: str
    _log_path: str

    level: InitVar[int] = logging.NOTSET  # 0~50
    mode: InitVar[str] = 'w'  # w: create new file, a: append
    logging_format: InitVar[logging.Formatter] = logging.Formatter(u'%(message)s')  # logging.Formatter(u'%(asctime)s|%(levelname)s|%(name)s|%(message)s')
    stream_handler_on: InitVar[bool] = False  # do you need to write text to console screen?
    stream_level: InitVar[int] = None  # 0~50

    def __post_init__(self, level, mode, logging_format, stream_handler_on, stream_level):
        work_dir = path.abspath(path.dirname(self.log_path))
        if not path.exists(work_dir):
            makedirs(work_dir)
        self._file_handler = logging.FileHandler(self.log_path, mode=mode, encoding='utf-8')
        self._file_handler.setFormatter(logging_format)
        self._file_handler.setLevel(level)

        self._log = logging.Logger(self.log_name)
        self._log.addHandler(self.file_handler)

        self._stream_handler = None
        if stream_handler_on:
            self._stream_handler = logging.StreamHandler()
            self._stream_handler.setLevel(stream_level)
            self._stream_handler.setFormatter(logging_format)
            self._log.addHandler(self.stream_handler)

    def __repr__(self):
        return self.log_path

    @property
    def log_name(self): return self._log_name

    @property
    def log_path(self): return self._log_path

    @property
    def log(self): return self._log

    @property
    def file_handler(self): return self._file_handler

    @property
    def stream_handler(self): return self._stream_handler


@dataclass(repr=False, eq=False)
class CLogging(_CLoggingBase):
    """
        * CLogging("log_name", "C:dir/xxx.log", level=0, mode='w', logging_format=logging.Formatter(u'%(message)s'), stream_handler_on=True, stream_level=logging.ERROR)
        * CLogging("log_name", "C:dir/xxx.log", logging.INFO, 'w', logging.Formatter(u'%(message)s'), True, logging.ERROR)
        * CLogging("log_name", "C:dir/xxx.log", logging.INFO, 'w', logging.Formatter(u'%(message)s'), True, logging.DEBUG)
        * CLogging("log_name", "temp_dir/xxx.log")

        logging_format::

            logging.Formatter(u'%(asctime)s|%(levelname)s|%(name)s|%(message)s')

        level::

            logging.CRITICAL)  # only state equ=critical will be write

            logging.NOTSET

        USAGE::

            import logging
            logging.basicConfig(level=logging.DEBUG, format=u'%(message)s')  # global variable setting. when logger is not defined then it's setting will use this.
            logger = logging.getLogger(__file__)
            # logger.setLevel(40)  # change level
            # logger.info('='*30 + ttf2ufo.__name__ + '='*30)
    """
    __slots__ = []

    def debug(self, msg):
        self.log.debug(msg)

    def info(self, msg):
        self.log.info(msg)

    def warning(self, msg):
        self.log.warning(msg)

    def error(self, msg):
        self.log.error(msg)

    def critical(self, msg):
        self.log.critical(msg)

    def show_msg_only_console(self, msg):
        if not self.stream_handler:
            return

        org_file_handler_level = self.file_handler.level
        org_stream_handler_level = self.stream_handler.level
        self._file_handler.setLevel(100)  # set level to highest, such that it will not write anything.
        self._stream_handler.setLevel(0)  # set level to lowest, such that it can be writing anything.
        self.error(msg)
        self._file_handler.setLevel(org_file_handler_level)
        self._stream_handler.setLevel(org_stream_handler_level)

    def close_logger(self):  # ref：https://stackoverflow.com/questions/24816456/python-logging-wont-shutdown
        self.log.removeHandler(self.file_handler)
        if self.stream_handler:
            self.log.removeHandler(self.stream_handler)
            del self._stream_handler
        del self._log, self._file_handler

    def close(self):
        self.close_logger()
