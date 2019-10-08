import logging
import sys
from functools import wraps

import nltk
from pydub import AudioSegment
from pydub.playback import play


class bcolor:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


"""func"""


def logged(level, name=None, message=None):
    """
    Add logging to a function. If name and message arent specified, they defau
    :param level: logging level, default value is INFO
    :param name: logger name, default value is function's module
    :param message: log message, default value is function's name
    :return:
    """

    def decorate(func):
        log_name = name if name else func.__module__
        logger = logging.getLogger(log_name)
        log_msg = message if message else func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.log(level, log_msg)
            return func(*args, **kwargs)

        return wrapper

    return decorate


def split_to_sentences(s):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    return tokenizer.tokenize(s)


def play_wav(wav_file):
    song = AudioSegment.from_wav(wav_file)
    play(song)


"""class"""


class Program:
    @staticmethod
    def debugging():
        gettrace = getattr(sys, 'gettrace', None)
        return (gettrace is not None) and gettrace()
