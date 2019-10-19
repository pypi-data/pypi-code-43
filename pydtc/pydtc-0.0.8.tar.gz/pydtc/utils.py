import time
import asyncio
from functools import wraps


def exec_time(logger=None):
    '''
    Decorator for module execution time.
    '''

    def timeit(f):
        @wraps(f)
        def timed(*args, **kwargs):
            ts = time.time()
            result = f(*args, **kwargs)
            te = time.time()
            if logger:
                logger.debug('[%r] execution time: %2.2f seconds' %
                             (f.__name__, (te-ts)))
            else:
                print('[%r] execution time: %2.2f seconds' %
                      (f.__name__, (te-ts)))
            return result
        return timed
    return timeit


def retry(*exceptions, retries=4, delay=4, logger=None):
    '''
    Decorator for function retry
    '''

    def deco_retry(f):
        @wraps(f)
        def inner(*args, **kwargs):
            mtries, mdelay = retries, delay
            while mtries > 0:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    mtries -= 1
                    msg = '%s, Retrying in %d seconds...' % (str(e), mdelay)

                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)

                    time.sleep(mdelay)

            return f(*args, **kwargs)
        return inner
    return deco_retry


def async_retry(*exceptions, retries=4, delay=4, logger=None):
    '''
    Decorator for async function retry.
    '''

    def deco_retry(f):
        @wraps(f)
        async def inner(*args, **kwargs):
            mtries, mdelay = retries, delay

            while mtries > 0:
                try:
                    return await f(*args, **kwargs)
                except exceptions as e:
                    mtries -= 1
                    msg = '{}, Retrying in {} seconds...'.format(
                        str(e), mdelay)

                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)

                    await asyncio.sleep(mdelay)

            return await f(*args, **kwargs)

        return inner
    return deco_retry
