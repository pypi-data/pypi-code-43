import sys
from asteval import Interpreter
aeval = Interpreter()

script = """
def tmp(x):
    return tmp(x+1)
##
"""

aeval(script)

for rec_limit in (50, 100, 200, 500, 1000, 2000, 5000, 10000):
    sys.setrecursionlimit(rec_limit)
    aeval('tmp(33)')
    msg = aeval.error_msg
    if msg is not None:
        print("rec limit=%d, length of error messge=%d" % (rec_limit,  len(msg)))
