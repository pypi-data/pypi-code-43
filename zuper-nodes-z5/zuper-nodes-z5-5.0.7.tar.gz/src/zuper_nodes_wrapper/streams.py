import os
import stat
import time
from io import BufferedReader

from zuper_commons.fs import make_sure_dir_exists
from . import logger_interaction
from . import logger

def wait_for_creation(fn):
    while not os.path.exists(fn):
        msg = 'waiting for creation of %s' % fn
        logger.info(msg)
        time.sleep(1)

def open_for_read(fin, timeout=None):
    t0 = time.time()
    # first open reader file in case somebody is waiting for it
    while not os.path.exists(fin):
        delta = time.time() - t0
        if timeout is not None and (delta > timeout):
            msg = f'The file {fin} was not created before {timeout} seconds. I give up.'
            raise EnvironmentError(msg)
        logger_interaction.info(f'waiting for file {fin} to be created')
        time.sleep(1)

    logger_interaction.info(f'Opening input {fin}')
    fi = open(fin, 'rb', buffering=0)
    # noinspection PyTypeChecker
    fi = BufferedReader(fi, buffer_size=1)
    return fi


def open_for_write(fout):
    if fout == '/dev/stdout':
        return open('/dev/stdout', 'wb', buffering=0)
    else:
        wants_fifo = fout.startswith('fifo:')
        fout = fout.replace('fifo:', '')

        logger_interaction.info(f'Opening output file {fout} (wants fifo: {wants_fifo})')

        if not os.path.exists(fout):

            if wants_fifo:
                make_sure_dir_exists(fout)
                os.mkfifo(fout)
                logger_interaction.info('Fifo created.')
        else:
            is_fifo = stat.S_ISFIFO(os.stat(fout).st_mode)
            if wants_fifo and not is_fifo:
                logger_interaction.info(f'Recreating {fout} as a fifo.')
                os.unlink(fout)
                os.mkfifo(fout)

        if wants_fifo:
            logger_interaction.info('Fifo detected. Opening will block until a reader appears.')

        make_sure_dir_exists(fout)
        fo = open(fout, 'wb', buffering=0)

        if wants_fifo:
            logger_interaction.info('Reader has connected to my fifo')

        return fo
