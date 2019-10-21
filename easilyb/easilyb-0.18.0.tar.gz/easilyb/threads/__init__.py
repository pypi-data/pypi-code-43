import threading
import queue


def threaded(func, args=None, kwargs=None, daemon=False):
    args = args or ()
    kwargs = kwargs or {}

    def wrapped(q, *a, **kw):
        ret = func(*a, **kw)
        q.put(ret)

    q = queue.Queue()
    if isinstance(args, tuple):
        args = (q,)+args
    else:
        args = [q,] + args
    t = threading.Thread(target=wrapped, args=args, kwargs=kwargs)
    t.setDaemon(daemon)
    t.start()
    t.result_queue = q
    return t
