import subprocess
import os
import time
import shlex
import json
from threading import Lock

import logging
logger = logging.getLogger(__name__)


DEFAULT_CMD_LOGFILE = "external_commands.log"
CMD_LOG_LOCK = Lock()


def run_command(command_line, log=False, log_file=None):
    if not isinstance(command_line, list):
        command_line = shlex.split(str(command_line))


    try:
        process = subprocess.Popen(command_line, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, )
        t0 = time.time()
        output, stderrdata =  process.communicate()
        return_code = process.poll()
        t1 = time.time()

        if log:
            if log_file is None:
                log_file = DEFAULT_CMD_LOGFILE
            mode = 'w'
            if os.path.isfile(log_file):
                mode = 'a'
            with CMD_LOG_LOCK:
                with open(log_file, mode) as fou:
                    #cmd_line = ' '.join(shlex.quote(x) for x in split_command)
                    fou.write(json.dumps({'cmd_line': ' '.join(command_line), 'return_code': return_code, 'output':output, 'start_time':t0, 'finish_time':t1})+'\n')
        return return_code, output
    except Exception as e:
        raise e


def run_command_ex1(command_line, log=False, log_file=None, yield_=False, timeout=None):

    if not isinstance(command_line, list):
        command_line = shlex.split(str(command_line))
    if isinstance(timeout, int) and timeout > 0:
        command_line = ['timeout', str(timeout)] + command_line
    logger.debug("Runinnng command: %s", command_line)

    process = subprocess.Popen(command_line, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, )
    t0 = time.time()
    output, stderrdata =  process.communicate()
    return_code = process.poll()
    t1 = time.time()

    if log:
        if log_file is None:
            log_file = DEFAULT_CMD_LOGFILE
        mode = 'w'
        if os.path.isfile(log_file):
            mode = 'a'
        with CMD_LOG_LOCK:
            with open(log_file, mode) as fou:
                #cmd_line = ' '.join(shlex.quote(x) for x in split_command)
                fou.write(json.dumps({'cmd_line': ' '.join(command_line), 'return_code': return_code, 'output':output, 'start_time':t0, 'finish_time':t1, 'timeout':timeout})+'\n')
    return return_code, output


def get_command_output(cmd_vector):
    p = subprocess.Popen(cmd_vector, stdout=subprocess.PIPE)
    return p.communicate()








