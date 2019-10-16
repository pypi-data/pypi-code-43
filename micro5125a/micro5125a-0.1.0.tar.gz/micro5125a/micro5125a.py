# -*- coding: utf-8 -*-

"""package micro5125a
author    Benoit Dubois
copyright FEMTO Engineering, 2019
license   GPL v3.0+
brief     Class to handle Microsemi (former Symmetricom, former Timing
          Solutions) 5125a device through its ethernet interface.
"""

import logging
import telnetlib


ACTION_LIST = ('start', 'stop', 'pause', 'resume', 'reset')
DATA_LIST = ('adev', 'state', 'spectrum', 'fcounter', 'spurs', 'phasediff',
             'inputs', 'ipn', 'timeconstant', 'tau0', 'phaserate')

CMD_PORT = 1299   # Command port
DATA_PORT = 1298  # Data port


# =============================================================================
class Micro5125A():
    """Class to handle Microsemi (former Symmetricom, former Timing Solutions)
    5125a device through its ethernet interface.
    """

    def __init__(self, ip):
        self._dev = telnetlib.Telnet()
        self.ip = ip

    def connect(self):
        """Connection process to command port of device.
        """
        self._dev.open(self.ip, CMD_PORT)
        # 5125A device begin (telnet) connection with a welcome message:
        # -> we ignore this message
        self.read_until('=' + self.ip + ' >')
        logging.debug("Connected to device (command port)")

    def connect_data_port(self):
        """Connection process to data port of device.
        """
        self._dev.open(self.ip, DATA_PORT)
        logging.debug("Connected to device (data port)")

    def disconnect(self):
        """Disconnection process.
        """
        self.write("^]")
        self._dev.close()
        logging.debug("Disconnected from device")

    def write(self, data):
        """Specific write method to send data to device.
        :returns: None
        """
        data = (data + '\n').encode('utf8')
        self._dev.write(data)
        logging.debug("write: %r", data)

    def read_all(self):
        """Read all data until EOF; block until connection closed.
        :returns: data read (str)
        """
        retval = self._dev.read_all()
        retval = retval.decode('utf8')
        logging.debug("read_all: %r", retval)
        return retval

    def read_very_eager(self):
        """Read all data until EOF; block until connection closed.
        :returns: data read (str)
        """
        retval = self._dev.read_very_eager()
        retval = retval.decode('utf8')
        logging.debug("read_very_eager: %r", retval)
        return retval

    def read_until(self, expected, timeout=None):
        """Read until a given string, expected, is encountered or
        until timeout seconds have passed.
        When no match is found, return whatever is available instead,
        possibly the empty string.
        :returns: data read (str)
        """
        expected = expected.encode('utf8')
        retval = self._dev.read_until(expected, timeout=timeout)
        retval = retval.decode('utf8')
        logging.debug("read_until: %r", retval)
        return retval

    def remote(self):
        """Takes remote control of the test set.
        :returns: None
        """
        self.write("control take")

    def local(self):
        """Yields remote control of the test set.
        :returns: None
        """
        self.write("control yield")

    def show_data(self, data_type):
        """Return current snapshot of data specified by 'data_type' parameter.
        :param data_type: a valid data type (see DATA_LIST) (str)
        :returns: snapshot of specified data type (str)
        """
        if data_type not in DATA_LIST:
            raise ValueError("Request bad data type: {}".format(data_type))
        self.write("show {}".format(data_type))
        retval = self.read_until('=' + self.ip + ' >')
        retval = retval.split('=' + self.ip + ' >')[0]
        return retval
