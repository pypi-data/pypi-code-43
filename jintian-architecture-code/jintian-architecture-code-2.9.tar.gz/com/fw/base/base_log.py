import os
import logging
from logging.handlers import TimedRotatingFileHandler
import time

if not os.path.exists('log'):
    os.mkdir('log')


def getLogger():
    log = logging.getLogger("pfw")

    formatter = logging.Formatter(
        '%(name)-12s %(asctime)s level-%(levelname)-8s thread-%(thread)-8d %(message)s')  # 每行日志的前缀设置
    fileTimeHandler = TimedRotatingFileHandler("./log/pfw.log" , "midnight", 1, 15)

    fileTimeHandler.suffix = "%Y%m%d.log"  # 设置 切分后日志文件名的时间格式 默认 filename+"." + suffix 如果需要更改需要改logging 源码
    fileTimeHandler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO)
    fileTimeHandler.setFormatter(formatter)
    log.addHandler(fileTimeHandler)
    return log

logger = getLogger()
