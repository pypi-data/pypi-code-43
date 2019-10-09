import time
import re
import sys
import io
import tempfile
import logging

import pexpect
from pexpect.spawnbase import SpawnBase


class SerialSpawn(SpawnBase):
    """Due to pyserial not support file descriptor for windows, fdspawn could not be used.
    This class implement a spawn for pyserial, all interfaces are defined from the base
    `SpawnBase`. For more information about the usage, please refer the pexpect documentation.

    Note: logfile_read detault is used in it's internal.

    Simple example:
        >>> ser = serial.Serial('COM3', 9600, timeout=0.1)
        >>> spawn = SerialSpawn(ser)
        >>> spawn.logfile = sys.stdout
        >>> spawn.write_expect("A", "Waiting for power mode select..", timeout=3)
        >>> print spawn.before
        >>> print spawn.after
        >>> spawn.expect([pexpect.EOF, pexpect.TIMEOUT], timeout=1)
        >>> spawn.close()
    """
    def __init__(self, serial, timeout=3, searchwindowsize=None,
            logfile=None, logfile_read=None, encoding=None, codec_errors='strict'):

        if not serial.is_open:
            serial.open()

        if hasattr(serial, 'reader_isalive'):
            if serial.reader_isalive:
                serial.stop_reader()
                logging.debug('reader thread is stopped!')

        self.serial = serial
        self.serial.timeout = 0.5
        super(SerialSpawn, self).__init__(
            timeout,
            searchwindowsize=searchwindowsize,
            logfile=logfile,
            encoding=encoding,
            codec_errors=codec_errors
        )

        self.logfile_read = logfile_read
        self.closed = not self.serial.is_open


    def read_nonblocking(self, size=1, timeout=None):
        """This is fake nonblocking, the size is decided by how many data in the buffer, rather than
        specific value, this is because big size will block the serial read, small size will effect the
        performance when many data in buffer. timeout is useless.
        """
        s = self.serial.read(self.serial.in_waiting or 1)
        s = self._decoder.decode(s, final=False)
        self._log(s, 'read')
        return s



    def send(self, s):
        """Send data to serial, and logging to log_send."""
        s = self._coerce_send_string(s)
        self._log(s, 'send')
        self._log("\n>>>%s\n"%s, 'read')
        b = self._encoder.encode(s, final=False)
        return self.serial.write(b)


    def sendline(self, s):
        """Send line"""
        s = self._coerce_send_string(s)
        return self.send(s + self.linesep)


    def write(self, s):
        self.send(s)


    def writelines(self, sequence):
        for s in sequence:
            self.write(s)



    def flush(self):
        self.serial.flush()


    def flush_log(self):
        if hasattr(self.serial, 'append_data') and isinstance(self.logfile_read, io.BytesIO):
            logging.debug("dump reading log to serial object!")
            self.logfile_read.seek(0)
            data = self.logfile_read.read()
            self.serial.append_data(data)



    def find(self, pattern, timeout=30):
        """Return the matches of pattern within a specific timeout
        in the serial reading stream. If EOF, return value is None.

        If timeout occured, that will raise pexpect.TIMEOUT exception.
        """
        try:
            self.expect(pattern, timeout=timeout)
            return self.before + self.after
        except pexpect.EOF:
            return None



    def test_input(self, input, expect, timeout=30):
        """Input value to serial, and test the output if match the expectation.

        Arguments:
            input {str} -- input string
            expect {str} -- pattern
            timeout {float} -- timeout in seconds

        Returns:
            str -- the output
        """
        self.write(input)
        self.expect(expect, timeout=timeout)
        self.flush_log()

        return self.before + self.after



    def close(self):
        """Close serial port, and dump the logfile_read to mcutk.pserial.Serial.data.
        If the serial instance is comes from pyserial, dump action will not take.
        """
        self.serial.close()
        self.flush_log()





    def isalive (self):
        return self.serial.is_open


