# -*- coding: utf-8 -*-

import itertools
import os
import signal
import psutil
import time
import random
import subprocess
import multiprocessing
from multiprocessing import Pool
from types import *
import datetime
import logzero
from logzero import logger
from time import ctime, sleep
import cdpchaosresource.utils
from cdpchaosresource.utils.ControllerThread import ControllerThread
from cdpchaosresource.utils.CPUActuator import CPUActuator
from cdpchaosresource.utils.MonitorThread import MonitorThread
from time import sleep
import itertools
import threading
from datetime import timedelta
import configparser
from configparser import ConfigParser

__all__ = ["create_cpu_load", "load_core"]

class ShutdownException(Exception):
    pass

def __sig_handler(*args):
    raise ShutdownException()

def create_cpu_load(input_path):

    path = input_path
    logger.info(f'Loading input argument from file path: {path}')
    config = ConfigParser()
    config.read(path)
    logger.debug(f'Configuration sections: {config.sections()}')

    if "cpu-attack" in config:
        core = int(config["cpu-attack"]["core"])
        cpu_load = int(config["cpu-attack"]["cpu_load"])
        duration_seconds = int(config["cpu-attack"]["duration_seconds"])
    sampling_interval = 0.1
    start_time=datetime.datetime.now()

    # list of cores 0-available
    core = [x for x in range(0,core)]
    cpu_load = itertools.repeat(cpu_load, len(core))

    # disable signal handlers before spawning processes
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    logger.info('Starting cpu attack at {}'.format(ctime()))
    logger.info('Current CPU statistics: [CPU cores={}], [CPU times={}], [CPU utilization={}]'.format(list(range(psutil.cpu_count())), psutil.cpu_times(), psutil.cpu_percent()))

    # spawn one process per core
    pool = multiprocessing.Pool(len(core))
    pool.map(load_core, list(zip(core
                                 , cpu_load
                                 , itertools.repeat(duration_seconds)
                                 , itertools.repeat(sampling_interval))))

    diff=datetime.datetime.now() - start_time
    logger.info('Stopped CPU attack after {0} seconds.'.format(diff))

def load_core(*args
              ):

    target_core=args[0][0]
    target_load=args[0][1]
    duration_seconds=args[0][2]
    sampling_interval=args[0][3]

    if duration_seconds >= 0:

        logger.info('Attacking core {} with a load of {}%  for {} seconds'.format(target_core, (target_load ), duration_seconds))
    else:
        logger.info('Attacking core {} with a load of {}% until interrupted'.format(target_core, (target_load )))

    if sampling_interval <= 0:
        logger.exception('Negative sampling interval!')

    target_load = target_load / 100

    # lock this process to the target core
    process = psutil.Process(os.getpid())
    process.cpu_affinity([target_core])

    monitor = MonitorThread(target_core, sampling_interval)
    control = ControllerThread(sampling_interval)
    control.set_cpu_target(target_load)

    actuator = CPUActuator(control, monitor,
                                      duration_seconds, target_core)

    signal.signal(signal.SIGINT, __sig_handler)
    signal.signal(signal.SIGTERM, __sig_handler)


    try:

        monitor.start()

        control.start()

        actuator.run()
        py_pid = psutil.Process(os.getpid())
        cpu_percent=py_pid.cpu_percent()
        logger.debug("The process {} is running on core: {}".format(py_pid, target_core))


    except ShutdownException:
        pass

    except:
        logger.exception('Encountered exception while trying to load CPU cores.')
        raise

    finally:
        # shutting down, so ignore any signals
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)

        actuator.close()

        monitor.stop()
        control.stop()

        monitor.join()
        control.join()
