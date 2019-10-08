"""
basic worker actor. but only works with thearding support.
"""
import threading
import time
import socket

__all__ = ['Worker']
hostname = socket.gethostname()


class Slot(object):
    """
    Queue style, a produce and consume slot.

    A synchronized slot class.
    """

    def __init__(self):
        self._slot = None
        self.mutex = threading.Lock()
        self._not_empty = threading.Condition(self.mutex)
        self._not_full = threading.Condition(self.mutex)

    def put(self, item):
        print("put")
        with self._not_full:
            while self._slot:
                print("still full")
                self._not_full.wait()
            self._slot = item
            print("put done")
            self._not_empty.notify()

    def get(self):
        print("get")
        with self._not_empty:
            while self._slot is None:
                print("still empty")
                self._not_empty.wait()
            item = self._slot
            self._slot = None
            self._not_full.notify()
            print("get done")
            return item


class WorkerExit(Exception):
    pass


class Worker(object):
    """
    basic worker of conductor, with no mailbox but a message slot.
    which means once a 
    """

    def __init__(self, index, executor, parent, wfcMgr):
        self.index = index
        self.wfcMgr = wfcMgr
        self.parent = parent
        self.executor = executor
        self._msg_slot = Slot()

    def start(self, *args, **kwargs):
        self._terminated = threading.Event()
        unit = threading.Thread(target=self._bootstrap, args=args, kwargs=kwargs)
        unit.daemon = True
        unit.start()

    def trigger(self, msg):
        self._msg_slot.put(msg)
        print("puuuut")

    def retrieve(self):
        msg = self._msg_slot.get()
        print("got")
        if msg is WorkerExit:
            raise WorkerExit()
        return msg

    def close(self):
        self.trigger(WorkerExit)

    def _bootstrap(self, *args, **kwargs):
        try:
            self.run(*args, **kwargs)
        except WorkerExit:
            pass
        finally:
            self._terminated.set()

    def join(self):
        self._terminated.wait()

    def run(self, *args, **kwargs):
        """
        basic partern is to retrieve msg from the slot and set to None.
        after the job done call callback method.
        """
        while True:
            print("before")
            task = self.retrieve()
            print("working")
            print(task)
            try:
                resp = self.executor(task, *args, **kwargs)
                if resp is None:
                    raise Exception('Task execution function MUST return a response as a dict with status and output fields')
                task['status'] = resp['status']
                task['outputData'] = resp['output']
                task['logs'] = resp['logs']
                self.wfcMgr.taskClient.updateTask(task)
            except Exception as err:
                print('Error executing task: ' + str(err))
                task['status'] = 'FAILED'
                self.wfcMgr.taskClient.updateTask(task)
            print("after")
            self.parent._callback(self.index)


if __name__ == "__main__":
    actor = Worker(0, print, print, 1)
    actor.start()
    actor.trigger("thrimbda")
    actor.close()
    actor.join()
