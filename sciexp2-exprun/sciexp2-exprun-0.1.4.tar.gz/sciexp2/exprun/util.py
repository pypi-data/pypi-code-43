#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2019, Lluís Vilanova"
__license__ = "GPL version 3 or later"


from contextlib import contextmanager
import joblib


@contextmanager
def step(message, logger=print):
    """Show simple progress messages around a piece of code.

    Parameters
    ----------
    message : str
        Message to print.
    logger : function, optinal
        Logging function. Defaults to `print`.

    Examples
    --------
    >>> with step("Doing something")
            print("some text")
    Doing something...
    some text
    Doing something... done

    """
    logger(message, "...")
    yield
    logger(message, "... done")


class threaded(object):
    """Context manager to run functions in parallel using threads.

    Examples
    --------
    Run two processes in parallel and wait until both are finished:

    >>> with step("Running in parallel"), threaded() as t:
            @t.start
            def f1():
                shell = LocalShell()
                shell.run(["sleep", "2"])
                print("f1")

            @t.start
            def f2():
                shell = LocalShell()
                shell.run(["sleep", "1"])
                print("f2")
    Running in parallel...
    f2
    f1
    Running in parallel... done

    """
    def __init__(self, n_jobs=None):
        if n_jobs is None:
            n_jobs = -1
        self._n_jobs = n_jobs
        self._jobs = []
        self.result = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pool = joblib.Parallel(backend="threading", n_jobs=self._n_jobs)
        self.result = pool(joblib.delayed(job, check_pickle=False)(*args, **kwargs)
        		   for job, args, kwargs in self._jobs)

    def start(self, target):
        """Decorator to start a function on a separate thread."""
        self._jobs.append((target, [], {}))

    def start_args(self, *args, **kwargs):
        """Callable decorator to start a function on a separate thread.

        Examples
        --------
        >>> with threaded() as t:
                @t.start_args(1, b=2)
                def f(a, b):
                    print(a, b)
        1, 2

        """
        def wrapper(target):
            self._jobs.append((target, args, kwargs))
        return wrapper


__all__ = [
    "step", "threaded",
]
