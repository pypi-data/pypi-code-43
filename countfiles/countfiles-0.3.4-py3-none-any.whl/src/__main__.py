import sys

import Countfiles

del sys.argv[0]
path = sys.argv[0] if len(sys.argv) else '.'
count = '--count' in sys.argv or '-c' in sys.argv
size = '--size' in sys.argv or '-s' in sys.argv
counter = Countfiles.Counter(
    path=path,
    count=count,
    size=size)
counter.call()
