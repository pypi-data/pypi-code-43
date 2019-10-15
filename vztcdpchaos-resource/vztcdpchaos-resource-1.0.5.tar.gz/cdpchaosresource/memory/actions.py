# -*- coding: utf-8 -*-

import itertools
import signal
import psutil
import time
import random
from types import *
import datetime
import logging
from time import ctime, sleep
from time import sleep
import os
import logzero
from logzero import logger
import configparser
from configparser import ConfigParser


####private function
def load_memory(memory):

    _ = [0] * int(((memory / 8) * (1024 ** 2)))
    py_pid = psutil.Process(os.getpid())
    logger.info('Usage statistics:: [PID={}], [Memory consumed={}], [CPU Utilization={}]',format(os.getpid(), py_pid.memory_info()[0]/2.**30, py_pid.cpu_percent()))

def create_mem_load(input_path):

    path = input_path
    logger.info(f'Loading input argument from file path: {path}')
    config = ConfigParser()
    config.read(path)
    logger.debug(f'Configuration sections: {config.sections()}')

    if "memory-attack" in config:
        memory = int(config["memory-attack"]["memory"])
        duration_seconds = int(config["memory-attack"]["duration_seconds"])



    start_time=datetime.datetime.now()
    logger.info('Starting memory attack at {}'.format(ctime()))
    logger.info('Current memory statistics={}'.format(dict(psutil.virtual_memory()._asdict())))

    mem_stats = psutil.virtual_memory()._asdict()
    mem_available = mem_stats['available']
    mem_toconsume_mb = (memory/100)* (6144)
    #mem_toconsume_mb = mem_toconsume_b / (1024 ** 2)




    if duration_seconds > 0:
        logger.info('Adding a load of {} % ({} MB) on the host '
              '{} seconds.'.format(memory, mem_toconsume_mb, duration_seconds))

    else:
        logger.info('Adding a load of {} % on the host '
              'until interrupted.'.format(memory))

    #rt = RepeatedTimer.RepeatedTimer(1, load_memory, memory)




    _ = [0] * int((mem_toconsume_mb / 8) * (1024 ** 2))
    py_pid = psutil.Process(os.getpid())

    try:
        if (duration_seconds > 0):
            time.sleep(duration_seconds)
        else:
            while 1:
                time.sleep(1)

    except MemoryError:
        logger.exception('Cannot allocate {} % of memory.'.format(memory))

    except KeyboardInterrupt:
        logger.error('User interrupted the process at {}'.format(ctime()))
    except:
        logger.exception('Encountered exception while trying to allocate memory.')

    finally:
        diff=datetime.datetime.now() - start_time
        #rt.stop()
        logger.info('Stopped memory attack after {} seconds.'.format(diff))
