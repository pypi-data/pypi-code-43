from typing import List

from f_tools.processing.task import Task


class Processor:
    """ Processor class
    This class is used to run multiprocessing tasks
    """

    def __init__(self, processes: List[Task]):
        self.processes = processes

    def run_parallel(self, wait=True):
        [p.start() for p in self.processes]
        if wait:
            [p.join() for p in self.processes]
