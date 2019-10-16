from matplotlib import pyplot
import time
import types
import collections

def argToStr(arg):
    if isinstance(arg, collections.abc.Sequence) and len(arg) > 3:
        return "[" + argToStr(arg[0]) + "," + argToStr(arg[1]) + ", ...]"
    else:
        return str(arg)

def evalWithTime(f, arg, c):
    s = f.__name__ + "(" + argToStr(arg) + ")"
    print("evaluating ", s, "... ", end="")
    start = time.time()
    for i in range(c):
        if isinstance(arg, tuple):
            f(*arg)
        else: 
            f(arg)
    et = (time.time() - start) / c
    print("finished in ", et, " seconds.")
    return et

def bench(f, args, measure=(lambda x: x), count=1):

    if not hasattr(f, '__call__'):
        raise TypeError("bench: first argument should be a function")
    if not isinstance(args, collections.abc.Sequence):
        raise TypeError("bench: second argument should be a series of arguments")
    x = [measure(i) for i in args]
    y = [evalWithTime(f,i,count) for i in args]
    return (x,y)

def plot(d, xlogscale=False, ylogscale=False):
    if xlogscale:
        pyplot.xscale("log")
    else:
        pyplot.xscale("linear")
    if ylogscale:
        pyplot.yscale("log")
    else:
        pyplot.yscale("linear")
    pyplot.plot(d[0],d[1])
    pyplot.show()

