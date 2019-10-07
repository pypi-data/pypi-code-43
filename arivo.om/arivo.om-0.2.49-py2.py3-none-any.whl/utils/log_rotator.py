import codecs
import os
import re
import subprocess
import threading
import time

from queue import Queue, Full, Empty


class LogRotator(object):
    def __init__(self, directory, prefix="hour_", flush_interval=60.0):
        self.directory = directory
        try:
            os.makedirs(self.directory)
        except:
            pass
        self.prefix = prefix
        self.file = None
        self.file_hour = None
        self.current_filename = None
        self.rotation_time = 3600
        self.flush_interval = flush_interval
        self.last_flush_time = 9999999999.9
        self.gzip_timestamp = time.time() - self.rotation_time / 60
        self.queue = None
        self.thread = None

    def get_hour(self):
        return int(time.time() / self.rotation_time)

    def filename(self, hour):
        return "{}{}.log".format(self.prefix, hour)

    def filepath(self, hour):
        return os.path.join(self.directory, self.filename(hour))

    def _open_file(self):
        try:
            if self.file:
                self.file.close()
        except:
            pass

        self.file_hour = self.get_hour()
        self.file = codecs.open(self.filepath(self.file_hour), "a", encoding="utf8")
        self.current_filename = self.filename(self.file_hour)
        self.last_flush_time = time.time()

    def gzip(self):
        for file in os.listdir(self.directory):
            if file.endswith(".log") and re.match(self.prefix + "\d+\.log",
                                                  file) and file != self.current_filename and not os.path.exists(
                    os.path.join(self.directory, file + ".gz")):
                subprocess.call("gzip {}".format(os.path.join(self.directory, file)), shell=True)

    def logrotate(self):
        if self.file:
            new_hour = self.get_hour()
            if new_hour != self.file_hour:
                self._open_file()
        else:
            self._open_file()

        if abs(time.time() - self.gzip_timestamp) > self.rotation_time / 60:
            self.gzip()

    def write(self, text, flush=False):
        self.logrotate()
        self.file.write(text)
        if flush or time.time() - self.last_flush_time > self.flush_interval:
            self.flush()

    def flush(self):
        if self.file:
            self.last_flush_time = time.time()
            self.file.flush()

    def run(self):
        while True:
            try:
                self.write(self.queue.get(timeout=max(0.0, self.last_flush_time+self.flush_interval-time.time())))
            except Empty:
                self.flush()

    def start_as_thread(self):
        if not self.queue:
            self.queue = Queue(maxsize=1000)
        if not self.thread:
            self.thread = threading.Thread(target=self.run)
            self.thread.setDaemon(True)
            self.thread.start()

    def put_on_queue(self, line):
        if self.queue:
            try:
                self.queue.put_nowait(line)
            except Full:
                return "Full"
        else:
            return "Not running"
        return ""
