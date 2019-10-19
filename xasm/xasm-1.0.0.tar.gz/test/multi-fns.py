#!/usr/bin/env python
x = lambda y: y + 1
z = lambda a: a + 2

def foo():
    def bar():
        return 5
    def baz():
        return 6
    return bar()

def bar():
    def baz():
        return 7
    return baz()

print(x(1))
print(z(1))
print(foo())
print(bar())
