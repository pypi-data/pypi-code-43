# -*- coding: utf-8 -*-

class Queued:
    """This class implements a simple FIFO queue. """

    def __init__(self):
        self._queue = []

    def put(self, item):
        self._queue.append(item)
        return

    def get(self):
        return self._queue.pop(0)

    def empty(self):
        return len(self._queue) == 0
