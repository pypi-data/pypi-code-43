'''my.log 파일과 스트림 로그를 생성하기 위한 파일입니다.'''
# https://stackoverflow.com/questions/7173033/duplicate-log-output-when-using-python-logging-module
import logging

loggers = dict()

def getMyLogger(name='basic'):
    global loggers

    # 로깅 기본 포멧 설정
    mylogger = logging.getLogger(name)
    if loggers.get(name):
        return loggers.get(name)

    formatter = logging.Formatter(
        '%(asctime)s - %(filename)s:%(lineno)s - %(funcName)s - %(levelname)s - %(message)s')
    mylogger.setLevel(logging.DEBUG)

    # 스트림 핸들러 설정
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARN)
    stream_handler.setFormatter(formatter)

    # 파일 핸들러 설정
    file_handler = logging.FileHandler(name + ".log", encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # 로깅 핸들러 추가
    mylogger.addHandler(file_handler)
    mylogger.addHandler(stream_handler)

    loggers[name] = mylogger

    return mylogger