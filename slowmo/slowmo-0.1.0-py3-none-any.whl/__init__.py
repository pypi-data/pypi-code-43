from contextlib import contextmanager
from dataclasses import dataclass, replace
from queue import Queue
from threading import Thread
from typing import Optional, Tuple

from slowmo.draw import draw
from slowmo.Status import Success
from slowmo.Task import Task
from slowmo.TaskTree import TaskTree


@dataclass
class State:
    root: TaskTree
    q: Queue
    thread: Thread
    path: Tuple = tuple()
    # TODO is path necessary? can we determine everything based on root?

    def __init__(self, tt: TaskTree):
        self.q = Queue()
        self.thread = Thread(target=draw, args=(self.q,))
        self.thread.start()
        self.path = tuple()
        self.root = tt
        self.q.put(self.root)

    def push(self, tt: TaskTree):
        ix = len(TaskTree.get_at(self.root, self.path).subtrees)
        self.root = TaskTree.replace_at(
            self.root, self.path, lambda st: TaskTree.add_subtree(st, tt)
        )
        self.path = self.path + (ix,)
        self.q.put(self.root)

    def pop(self):
        self.root = TaskTree.replace_at(
            self.root,
            self.path,
            lambda st: TaskTree(Task.replace_status(st.task, Success()), st.subtrees),
        )
        self.path = self.path[:-1]
        self.q.put(self.root)

    def close(self):
        # `None` is a sentinel value to stop drawing
        self.q.put(None)


s: Optional[State] = None


@contextmanager
def task(msg: str):
    global s
    t = Task(description=msg)
    tt = TaskTree(t)
    is_root = False
    if s is None:
        is_root = True
        s = State(tt)
        # TODO capture input?
    else:
        s.push(tt)
    yield
    s.pop()

    if is_root:
        s.close()
        s = None


if __name__ == "__main__":
    from time import sleep

    with task("main task"):
        sleep(1)
        with task("subtask 1"):
            sleep(2)
            with task("subtask 1a"):
                sleep(2)
        with task("subtask 2"):
            sleep(3)
        sleep(1)
