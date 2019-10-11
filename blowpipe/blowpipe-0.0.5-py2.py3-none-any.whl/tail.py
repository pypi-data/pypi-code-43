import time


class Tail:
    def __init__(self, filename, sleep=1):
        self.filename = filename
        self.sleep = sleep
        self._quit = False

    def stop(self):
        self._quit = True

    def start(self):
        f = open(self.filename, 'r')
        try:
            f.seek(0, 2)
            while not self._quit:
                current_position = f.tell()
                line = f.readline()
                if not line:
                    f.seek(current_position)
                    time.sleep(self.sleep)
                else:
                    yield line
            return None
        finally:
            f.close()
