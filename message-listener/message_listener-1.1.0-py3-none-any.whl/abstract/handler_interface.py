#!/usr/bin/python3
# pylint: disable=I0011,R0913,R0902
"""Define Handler abstact"""


class Handler(object):
    """Handler abstract"""
    def __init__(self, *argv):
        self.workers = []
        for worker in argv:
            self.workers.append(worker)

    def add_worker(self, worker):
        self.workers.append(worker)

    def handle(self, message):
        """handle a message"""
        raise NotImplementedError("handle not implemented")
