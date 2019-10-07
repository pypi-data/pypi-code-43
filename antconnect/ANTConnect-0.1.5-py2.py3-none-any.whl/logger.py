import time
import datetime


class Logger:
    _on = False

    def on(self):
        self._on = True

    def off(self):
        self._on = False

    def toggle(self):
        self._on = self._on

    def log(self, message, add_timestamp=True):
        if self._on:
            if add_timestamp:
                value = datetime.datetime.fromtimestamp(time.time())
                readable_time = value.strftime("%Y-%m-%d %H:%M:%S")
                print("[{}] {}".format(readable_time, message))
            else:
                print(message)
