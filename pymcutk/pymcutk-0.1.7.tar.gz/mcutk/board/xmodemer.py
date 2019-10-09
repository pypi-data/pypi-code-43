import os
import sys
import time
import logging
import serial
from xmodem import XMODEM

from mcutk.exceptions import SerialCannotOpenException


def loadfile(serialo, filename, ctrltext='x'):
    """Flash programming with serial based on xmodem protocl.

    Arguments:
        serialo {serial.Serial object} -- an serial.Serial object
        filename {str} -- path to file.
        ctrltext {str} -- the string will be written to serial to control the loader mode.
                        default is 'x'

    Exceptions:
        SerialCannotOpenException -- raise when serial cannot be open

    Returns:
        boolean -- There is no error, it will return True, else False.
    """

    if not serialo.is_open:
        serialo.open()

    cnt, dat = 0, ""

    logging.info("checking serial output")
    # read data when 'READY' is in the context, or timeout.
    while True:
        n = serialo.inWaiting()
        dat = serialo.read(n)

        # logging the serial ouput
        if dat != "":
            logging.info("\n" +dat)

        # check string
        if "READY" in dat:
            break

        # check timeout
        if cnt > 60:
            logging.warning("Timeout: not found 'READY' in serial output..")
            serialo.close()
            return False

        cnt = cnt + 1
        time.sleep(1)


    def getc(size, timeout=10):
        return serialo.read(size)


    def putc(data, timeout=10):
        sys.stdout.write('=')
        serialo.write(data, log=False)
        time.sleep(0.001)

    serialo.write(ctrltext)
    logging.info("> Download program via XMODEM protocol: %s", filename)

    result = False
    with open(filename, 'rb') as stream:
        modem = XMODEM(getc, putc)
        result = modem.send(stream, retry=4)
        serialo.close()

    if result:
        logging.info("Flash successful")
    else:
        logging.warning("Flash failure!!!")

    return result

def loadfile_delayed(serialo, filename, ctrltext='x', delay=1):
    """Flash programming with serial based on xmodem protocl.

    Arguments:
        serialo {serial.Serial object} -- an serial.Serial object
        filename {str} -- path to file.
        ctrltext {str} -- the string will be written to serial to control the loader mode.
                        default is 'x'
		delay {number} -- delay time in second

    Exceptions:
        SerialCannotOpenException -- raise when serial cannot be open

    Returns:
        boolean -- There is no error, it will return True, else False.
    """

    if not serialo.is_open:
        serialo.open()

    cnt, dat = 0, ""
    logging.info("checking serial output")
    delay = delay + 10
    # read data when 'READY' is in the context, or timeout.
    while True:
        n = serialo.inWaiting()
        dat = serialo.read(n)

        # logging the serial ouput
        if dat != "":
            logging.info("\n" +dat)

        # check string
        if "READY" in dat:
            break

        # check timeout
        if cnt > delay:
            logging.warning("Timeout: not found 'READY' in serial output..")
            break

        cnt = cnt + 1
        time.sleep(1)

    logging.info("delay %s s", delay)
    #time.sleep(delay)
    def getc(size, timeout=10):
        return serialo.read(size)


    def putc(data, timeout=10):
        sys.stdout.write('=')
        serialo.write(data, log=False)
        time.sleep(0.001)

    serialo.write(ctrltext)
    logging.info("> Download program via XMODEM protocol: %s", filename)

    result = False
    with open(filename, 'rb') as stream:
        modem = XMODEM(getc, putc)
        result = modem.send(stream, retry=4)
        serialo.close()

    if result:
        logging.info("Flash successful")
    else:
        logging.warning("Flash failure!!!")

    return result


