''' decoupled: run a function in a different process '''

# pylint: disable=keyword-arg-before-vararg
# This is the order decorator needs

import multiprocessing
import queue

from decorator import decorator
from tblib import Traceback


@decorator
def decoupled(func, timeout=None, *args, **kwargs):
    ''' run a function in a different process '''
    result_queue, process = run_subprocess(func, args, kwargs, timeout)

    try:
        return determine_result(result_queue, process)
    finally:
        process.terminate()


def run_subprocess(func, args, kwargs, timeout):
    '''
    run func in a separate process and waits for it to terminate
    (one way or another)
    returns a tuple (result_queue, process), where...
    - result_queue is used to communicate return value / exceptions thrown
    - process is the actual process object
    '''
    result_queue = multiprocessing.Queue()

    process = multiprocessing.Process(
        target=proc,
        args=(result_queue, func, args, kwargs))
    process.start()
    process.join(timeout=timeout)

    return result_queue, process


def proc(result_queue, func, args, kwargs):
    ''' This is what's run in the other process. '''
    try:
        result_queue.put({'returnValue': func(*args, **kwargs)})
    except Exception as err:  # pylint: disable=broad-except
        result_queue.put({
            'err': err,
            'traceback': Traceback(err.__traceback__).to_dict()})


def determine_result(result_queue, process):
    '''
    Find out what happened in the subprocess
    and return/raise accordingly
    '''
    if process.exitcode is None:
        raise ChildTimeoutError

    try:
        retval = result_queue.get(timeout=0)
        if 'returnValue' in retval.keys():
            return retval['returnValue']
        raise retval['err'].with_traceback(
            Traceback.from_dict(retval['traceback']).as_traceback())
    except queue.Empty:
        raise ChildCrashedError
    raise ValueError('This should not be reachable - but pylint thinks it is.')


class ChildTimeoutError(Exception):
    ''' thrown when the child process takes too long '''


class ChildCrashedError(Exception):
    ''' thrown when the child process crashes '''
