import os
import logging
import pika
import time
import threading
import json
import sys
import tempfile
from pathlib import Path
from logging.handlers import RotatingFileHandler
from jsonschema import validate
from  micropipes.shared.namegen import random_name
from functools import wraps
this_dir, this_filename = os.path.split(__file__)

LOG_APP = 'app'
LOG_PERF = 'perf'
LOG_OTHERS = 'others'

MAX_CONNECTION_RETRIES = 100
ENV_MQ_HOST = 'RABBITMQ_HOST'
ENV_MQ_USER = 'RABBITMQ_USER'
ENV_MQ_PASS = 'RABBITMQ_PASS'
# when we are under k8, this is automatically propagated - use this one
ENV_MICROPIPES_RABBITMQ_SERVICE_HOST = 'MICROPIPES_RABBITMQ_SERVICE_HOST'
ENV_LIVENESS_PROBE_FILE = 'LIVENESS_PROBE_FILE'


LOG = logging.getLogger(LOG_APP)
PLOG = logging.getLogger(LOG_PERF)

def track_uuid():
    # return uuid.uuid1().int >> 64
    # return uuid.uuid1().hex
    return random_name()


def sorted_dir(folder, rev=False):
    def getmtime(name):
        path = os.path.join(folder, name)
        return os.path.getmtime(path)
    if not os.path.exists(folder):
        return []
    return sorted(os.listdir(folder), key=getmtime, reverse=rev)


def get_latest_checked(folder, suffix):
    content = sorted_dir(folder, rev=True)
    for f in content:
        if not f.endswith(suffix):
            continue
        basename = os.path.splitext(f)[0]
        full_name = os.path.join(folder, basename + '.json')
        if os.path.exists(full_name):
            return full_name, basename
    return None, None

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))



def perf(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        t1 = time.time()
        rt = f(*args, **kwargs)
        PLOG.debug("{}() {:.4f} ms.".format(f.__name__,(time.time() - t1) * 1000.0))
        return rt
    return decorated


log_env_initialized_lock = threading.Lock()
log_env_initialized = False

def setup_log_env():
    global log_env_initialized, log_env_initialized_lock
    if not log_env_initialized:
        try:
            log_env_initialized_lock.acquire()
            if log_env_initialized:
                return
            loglevel_app = 'INFO'
            loglevel_perf = 'INFO'
            loglevel_others = 'WARNING'

            if 'LOG_LEVEL' in os.environ:
                llev = os.environ['LOG_LEVEL']
                if llev.find('-') != -1:
                    levels = llev.split('-')
                else:
                    levels = llev.split(',')
                if len(levels) > 0:
                    loglevel_app = levels[0]
                if len(levels) > 1:
                    loglevel_perf = levels[1]
                if len(levels) > 2:
                    loglevel_others = levels[2]
            conf = {
                "log": {
                    "app": loglevel_app,
                    "perf": loglevel_perf,
                    "others": loglevel_others,
                }
            }
            setup_log(conf, just_console=True)
            log_env_initialized = True
        finally:
            log_env_initialized_lock.release()



class _MaxLevelFilter(object):
    def __init__(self, highest_log_level):
        self._highest_log_level = highest_log_level

    def filter(self, log_record):
        return log_record.levelno <= self._highest_log_level

def create_logger(log_type, conf, format,  just_console = False):
    logger = logging.getLogger(log_type)
    logger.setLevel(conf['log'][log_type])
    if just_console:
        log_out = logging.StreamHandler(sys.stdout)
        log_out.addFilter(_MaxLevelFilter(logging.WARNING))
        log_err = logging.StreamHandler(sys.stderr)
        log_err.setLevel(logging.ERROR)
        logger.addHandler(log_err)
    else:
        log_out = RotatingFileHandler( os.path.join( conf['log']['logdir'],conf['log']['logfileprefix']+'.'+ log_type+'.log' ),
                                maxBytes=conf['log']['logmaxbytes'], backupCount=conf['log']['logcount'])
    log_out.setLevel(conf['log'][log_type])
    log_out.setFormatter(logging.Formatter(format))
    logger.addHandler(log_out)


def setup_log(conf, just_console = False):
    create_logger(LOG_OTHERS, conf,'%(asctime)s - %(levelname)s - %(filename)s.%(funcName)s %(message)s',just_console)
    create_logger(LOG_APP, conf,'%(asctime)s - %(levelname)s - %(filename)s.%(funcName)s %(message)s',just_console)
    create_logger(LOG_PERF, conf,'%(asctime)s - PERF - %(filename)s.%(funcName)s %(message)s',just_console)



def create_mq_connection( max_connection_retries = MAX_CONNECTION_RETRIES):
    LOG.debug('Creating mq connection')
    host = None
    if ENV_MICROPIPES_RABBITMQ_SERVICE_HOST in os.environ:
        host = os.environ[ENV_MICROPIPES_RABBITMQ_SERVICE_HOST]
    else:
        host = None if not ENV_MQ_HOST in os.environ else os.environ[ENV_MQ_HOST]
    user = 'guest' if not ENV_MQ_USER in os.environ else os.environ[ENV_MQ_USER]
    password = 'guest' if not ENV_MQ_PASS in os.environ else os.environ[ENV_MQ_PASS]
    cred = pika.credentials.PlainCredentials(
        user, password)
    ret = None
    connected = False
    retry = 0
    while not connected:
        try:
            retry += 1
            ret = pika.BlockingConnection(
                pika.ConnectionParameters(host=host, credentials=cred))
            connected = True
        except Exception as e:
            if retry > max_connection_retries:
                LOG.error('No connection')
                return None
            LOG.warning(e)
            LOG.warning('Trying to reconnect to {} {} {}'.format(host,user,password))
            time.sleep(2)
    return ret

def close_mq_connection(connection):
    LOG.debug('Closing mq connection')
    try:
        connection.close()
    except Exception as e:
        LOG.error(e, exc_info=True)


schema_loading_lock = threading.Lock()
schema_loaded = None

def get_job_schema():
    global schema_loading_lock, schema_loaded
    if not schema_loaded:
        try:
            schema_loading_lock.acquire()
            schema = os.path.join(this_dir,'job.schema.json')
            with open(schema, 'r') as f:
                schema_loaded = json.load(f)
        finally:
            schema_loading_lock.release()
    return schema_loaded


def validate_job_schema(json_data):
    validate(json_data, get_job_schema())


def touchLivenessProbe():
    if not ENV_LIVENESS_PROBE_FILE in os.environ:
        return
    envf = os.environ[ENV_LIVENESS_PROBE_FILE]
    directory = os.path.dirname(envf)
    if not os.path.exists(directory):
        os.makedirs(directory)
    Path(envf).touch()

def dump_file(fname ):
    directory = tempfile.gettempdir()
    directory = os.path.join(directory, 'micropipes')
    if not os.path.exists(directory):
        os.makedirs(directory)
    fname = os.path.join(directory, fname)
    # LOG.debug(fname)
    return open(fname, 'w')

def create_stats_job_entry(worker_type, worker_id, customer_id, job_id, stats_name, stats_value):
    return {
        'time': time.time(),
        'worker_type': worker_type,
        'worker_id': worker_id,
        'customer_id': customer_id,
        'job_id': job_id,
        'stats_name': stats_name,
        'stats_value': stats_value
    }

def create_stats_customer_entry( worker_type, worker_id, customer_id, stats_name, stats_value):
    return {
       'time': time.time(),
       'worker_type': worker_type,
       'worker_id': worker_id,
       'customer_id': customer_id,
       'stats_name': stats_name,
       'stats_value': stats_value
    }