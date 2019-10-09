from __future__ import absolute_import
from functools import partial
import io
import time
import logging

from serial import Serial as PY_SERIAL
from serial.threaded import Protocol, ReaderThread
from mcutk.pserial.serialspawn import SerialSpawn


class DataHandler(Protocol):
    """Data handler for ReaderThread."""

    def connection_made(self, transport):
        super(DataHandler, self).connection_made(transport)
        self._serial = transport.serial

    def data_received(self, data):
        if data:
            self._serial._data.append(data)



class Serial(PY_SERIAL):
    """This class is inherited from pyserial::serial.Serial class.
    It extended the Serial class to support data reading in a background thread.

    The attribute serial.reader is the instance of reading thread.
    """

    def __init__(self, *args, **kwargs):
        if not kwargs.get('timeout', None):
            kwargs['timeout'] = 1
        super(Serial, self).__init__(*args, **kwargs)
        self._data = list()
        self.reader = None
        # enable serialspawn, default logfile_read is memory
        self.Spawn = partial(SerialSpawn, self, logfile_read=io.BytesIO())
        self.SerialSpawn = self.Spawn

    def write(self, data, log=True):
        """write data"""
        if log:
            logging.info("%s write: %s", self.port, repr(data))
        super(Serial, self).write(data)

    def write_chars(self, data, interval=0.03):
        """Send char one by one in a string with a fixed interval.

        Arguments:
            data {str} -- input data
            interval {float} -- interval seconds (default: {0.03})
        """
        for s in data:
            self.write(s)
            time.sleep(interval)

    def start_reader(self):
        """Start the reader thread, and return the data handler when the reader is running.
        If the port is not open, it will open it at first.
        """
        if not self.is_open:
            self.open()

        if self.reader_isalive:
            raise RuntimeError('failed to start reader, reader thread is already running.')

        self.reader = ReaderThread(self, DataHandler)
        data_handler = self.reader.__enter__()
        logging.info('%s reading thread is running!', self.port)
        return data_handler


    def stop_reader(self):
        """Stop the reader thread."""
        if self.reader_isalive:
            self.reader.stop()
            logging.info('%s reading thread is stopped!', self.port)


    def clear_reader_buffer(self):
        """Clear the data buffer for the reader thread.
        """
        self._data = list()


    @property
    def reader_isalive(self):
        """Return a boolean value to identify the reader is alive or not.
        """
        return self.reader and self.reader.alive



    @property
    def data(self):
        """Return all of data in the internal data buffer."""
        return "".join(self._data)


    def append_data(self, data):
        """Append data to internal buffer."""
        self._data.append(data)



    def close(self):
        """Close the serial port.
        """
        if self.reader and self.reader.alive:
            self.stop_reader()
        super(Serial, self).close()

