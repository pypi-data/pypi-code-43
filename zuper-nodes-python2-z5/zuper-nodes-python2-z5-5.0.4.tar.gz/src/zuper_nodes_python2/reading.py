import io
import time
from . import logger
import select
import cbor2 as cbor
# Python 2 compatibility.
try:
    TimeoutError
except NameError:
    import socket
    TimeoutError = socket.timeout

def wait_for_data(f, timeout=None, waiting_for = None):
    """ Raises StopIteration if it is EOF.
            Raises TimeoutError if over timeout"""
    # XXX: StopIteration not implemented
    fs = [f]
    t0 = time.time()
    intermediate_timeout = 3.0

    while True:
        try:
            readyr, readyw, readyx = select.select(fs, [], fs, intermediate_timeout)
        except io.UnsupportedOperation:
            break
        if readyr:
            break
        elif readyx:
            logger.warning('Exceptional condition on input channel %s' % readyx)
        else:
            delta = time.time() - t0
            if (timeout is not None) and (delta > timeout):
                msg = 'Timeout after %.1f s.' % delta
                logger.error(msg)
                raise TimeoutError(msg)
            else:
                msg = 'I have been waiting %.1f s.' % delta
                if timeout is None:
                    msg += ' I will wait indefinitely.'
                else:
                    msg += ' Timeout will occurr at %.1f s.' % timeout
                if waiting_for:
                    msg += ' ' + waiting_for
                logger.warning(msg)


def read_next_cbor(f, timeout=None, waiting_for = None):
    """ Raises StopIteration if it is EOF.
        Raises TimeoutError if over timeout"""
    wait_for_data(f, timeout, waiting_for)

    try:
        j = cbor.load(f)
        return j
    except OSError as e:
        if e.errno == 29:
            raise StopIteration
        raise
