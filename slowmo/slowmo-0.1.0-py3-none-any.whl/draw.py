from itertools import cycle
from queue import Queue
from time import sleep
import sys

from blessed import Terminal
from spinners import Spinners

from slowmo.TaskTree import TaskTree
import slowmo.terminal as terminal


spinner = cycle(Spinners.dots.value["frames"])
refresh_rate_seconds = 0.06


def draw(q: Queue, erase=True):
    """Formats task trees within the terminal window.

    Args:
        q: Queue of task trees to draw.
    """
    term = Terminal()
    write = sys.stdout.write

    tt: TaskTree = q.get()
    while True:
        with term.cbreak():
            if not q.empty():
                while not q.empty():
                    # get latest task tree, ignore intermeditate task trees
                    tt = q.get()
                if tt is None:
                    # `None` is a sentinel value to stop drawing
                    if not erase:
                        print(TaskTree.display(tt))
                    break

                tt_size = TaskTree.size(tt)
                if tt_size > term.height:
                    # TODO: how to handle task trees too large to fit in window?
                    raise NotImplementedError()

                # TODO: fix bug in vacant code. seems to be an off-by-1 error somewhere...
                row, _ = terminal.location(term)
                vacant = term.height - row
                if vacant < tt_size:
                    # make room
                    overflow = tt_size - vacant
                    write(terminal.move_row(term, term.height - 1))
                    write("\n" * overflow)
                    write(terminal.move_row(term, term.height - tt_size))

            row, _ = terminal.location(term)
            print(TaskTree.display(tt, spinner=next(spinner)))
            sleep(refresh_rate_seconds)
            write(terminal.move_row(term, row))
            write(term.clear_eos)
