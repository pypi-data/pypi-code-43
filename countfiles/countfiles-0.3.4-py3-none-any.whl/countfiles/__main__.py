import sys

from . import core

del sys.argv[0]

options = {}
if '--count' in sys.argv or '-c' in sys.argv:
    options['count'] = True
if '--size' in sys.argv or '-s' in sys.argv:
    options['size'] = True

i = 0
while i < len(sys.argv):
    if sys.argv[i].startswith('-'):
        del sys.argv[i]
    else:
        i += 1

counter = core.Counter(
    path=sys.argv[0] if len(sys.argv) else '.',
    **options)
print(counter.call())
