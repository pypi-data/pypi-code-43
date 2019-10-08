import sys

def error_output(*x):
    print(*x, file=sys.stderr)

def output(*x):
    print(*x)