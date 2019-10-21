# appteka - helpers collection

# Copyright (C) 2018-2019 Aleksandr Popov

# This program is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Lesser GNU General Public License for more details.

# You should have received a copy of the Lesser GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Writing data to IO text buffer using queue and working in separate
thread."""


from collections import deque
from threading import Thread, Lock, Event
from time import sleep
from warnings import warn


class QueuedWriter:
    """Tool for record data to text buffer using queue and thread."""
    def __init__(self, buff=None, write_on='time', write_every=1):
        self._buff = buff
        self._queue = deque([])
        self._thread = None
        self._thread_args = (self._save_queue, write_on, write_every)
        self._convert_func = lambda x: x

    def set_buff(self, buff):
        """Set IO buffer."""
        self._buff = buff

    def set_convert_func(self, func):
        """Set function for convertion data sample to string."""
        self._convert_func = func

    def start_thread(self):
        """Start recording thread."""
        self._thread = PyRecordThread(*self._thread_args)
        self._thread.start()

    def start_record(self):
        """Deprecated."""
        warn("start_record() is deprecated. Use start_thread().")
        self.start_thread()

    def add_data(self, sample):
        """Add data sample."""
        self._queue.append(sample)
        self._thread.write_data()

    def _save_queue(self):
        """Move data from queue to buffer."""
        while self._queue:
            sample = self._queue.popleft()
            line = self._convert_func(sample)
            self._buff.write(line)

    def stop_thread(self):
        """Stop recording record."""
        self._thread.write_data()
        self._thread.stop()

    def stop_record(self):
        """Deprecated."""
        warn("stop_record() is deprecated. Use stop_thread().")
        self.stop_thread()


class PyRecordThread(Thread):
    """Thread in which samples recorded to IO buffer."""
    def __init__(self, save_func, write_on='time', write_every=1):
        super().__init__()
        self._lock = Lock()
        self._must_write = False
        self._can_quit = Event()
        self._have_data = Event()
        self.save_func = save_func
        if write_on == 'time':
            self._loop_func = self._sleep_loop
            self._loop_func_args = (write_every, )
        elif write_on == 'data':
            self._loop_func = self._event_loop
            self._loop_func_args = ()
        else:
            raise RuntimeError("write_on must be 'time' or 'data'.")

    def run(self):
        """Record data from queue to buffer."""
        self._can_quit.clear()
        with self._lock:
            self._must_write = True
        self._loop_func(*self._loop_func_args)
        self._can_quit.set()

    def _sleep_loop(self, period):
        while self._must_write:
            sleep(period)
            self.save_func()

    def _event_loop(self):
        while self._must_write:
            self._have_data.clear()
            self._have_data.wait()
            self.save_func()

    def write_data(self):
        """Ask thread to write data."""
        self._have_data.set()

    def stop(self):
        """Stop thread."""
        with self._lock:
            self._must_write = False
        self._can_quit.wait()
        self.join()


def _example():
    from random import randint

    def convert_func(sample):
        """Convert function."""
        return '{}: {}\n'.format(*sample)

    writer = QueuedWriter(write_on='time')
    writer.set_convert_func(convert_func)
    buf = open('output.txt', 'w')
    writer.set_buff(buf)
    writer.start_thread()

    i = 0
    while True:
        try:
            sample = (i, randint(0, 100))
            print(sample)
            writer.add_data(sample)
            sleep(0.02)
            i += 1
        except KeyboardInterrupt:
            print("Good bye...")
            break

    writer.stop_thread()
    buf.close()


if __name__ == "__main__":
    _example()
