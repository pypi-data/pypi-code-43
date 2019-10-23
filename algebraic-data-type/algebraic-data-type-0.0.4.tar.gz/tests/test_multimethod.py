from ..adt import Multimethod, _

with Multimethod() as fib:
    fib[1] = 1
    fib[2] = 1
    fib[int] =  lambda x: fib(x-1) + fib(x-2)

def test_multimethod():
    assert(fib(1) == 1)
    assert(fib(2) == 1)
    assert(fib(3) == 2)
    assert(fib(4) == 3)