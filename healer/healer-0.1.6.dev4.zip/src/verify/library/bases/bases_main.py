

class A(object):

    def f(self):
        print("A.f()")


class B (A):

    def g(self):
        print("B.g()", end=": ")
        super(B, self).f()


class C(object):

    def f(self):
        print("C.f()")


B.__bases__ = (C,)
b = B()
b.g()

A.__bases__ = (C,)  # TypeError: __bases__ assignment: 'C' deallocator differs from 'object'

