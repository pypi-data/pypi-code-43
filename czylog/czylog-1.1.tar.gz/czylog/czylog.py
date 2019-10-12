'''
@File       : czylog.py
@Copyright  : Rainbol
@Date       : 2019/9/25
@Desc       :
'''
import logging
import os
import platform
import re
from logging import handlers

default_log_level = 'debug'


class SingletonLog(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance


class RainLog(SingletonLog):

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, log_where, logs_level='debug', backCount=5, when='D', interval=1):
        '''log_where日志绝对路径,logs_level日志等级'''
        self.level = logs_level
        self.logger = logging.getLogger('rainlog')  # 拿到一个logger对象
        self.stream = logging.StreamHandler()  # 创建一个屏幕输出对象
        fmt = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')  # 定义日志格式
        if not os.path.isabs(log_where):
            log_where = os.path.abspath(log_where)
        self.bl = handlers.TimedRotatingFileHandler(filename=log_where, when=when, interval=interval,
                                                    backupCount=backCount,
                                                    encoding='utf-8')

        self.bl.setFormatter(fmt)  # fh文件添加输出格式
        self.stream.setFormatter(fmt)  # ch屏幕添加输出格式
        # 为logger添加文件输出格式和屏幕输出格式
        self.logger.addHandler(self.stream)
        self.logger.addHandler(self.bl)
        self.logger.setLevel(getattr(logging, self.level.upper()))  # 指定日志级别设置为DEBUG

    def write(self, connect):
        '''写日志,connect:写入信息'''
        if self.level.lower() == default_log_level.lower():
            res = getattr(self.logger, self.level.lower(), 'debug')
            res(connect)
            #  添加下面一句，在记录日志之后移除句柄
            self.logger.removeHandler(self.stream)
            self.logger.removeHandler(self.bl)
        else:
            pass

    def split_plus(self, path):
        '''全路径分割'''
        if platform.system().lower() == 'linux':
            return path.split(os.path.sep)
        else:
            return path.split(os.path.sep)[1:]

    def little_regular(self, args, files_str):
        ''' 只支持'.','*','?'格式路径,小型blog模块 args:过滤文件 或者 文件夹 名称,files_str:文件路径 '''
        _list = ''
        for l in args:
            if l in ['/', '\\', '\\\\']:
                raise ('不支持完整路径')
            if l == '*':
                l = '.*'
            elif l == '?':
                l = '.'
            else:
                pass
            _list = _list + l
        res = re.findall(_list, files_str)
        if not res: return None
        l = self.split_plus(files_str)
        for y in res:
            if os.path.split(y)[1] in l:
                return True
            else:
                return None


if __name__ == '__main__':
    # logger = RainLog('your_path')
    # logger.write('your_message')
    pass
