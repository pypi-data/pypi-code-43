import numpy
from chaospy.polynomial import npoly, Polynomial, variable

q0, q1 = variable(2)


def test_numpy_sum():
    poly = npoly([[1, 5*q0], [q0+3, -q1]])
    assert numpy.sum(poly) == -q1+q0*6+4
    assert numpy.all(numpy.sum(poly, axis=0) == npoly([q0+4, -q1+q0*5]))
    assert numpy.all(
        numpy.sum(poly, axis=-1, keepdims=True) == npoly([[q0*5+1], [q0-q1+3]]))


def test_numpy_any():
    poly = npoly([[0, q1], [0, 0]])
    assert numpy.any(poly)
    assert numpy.all(numpy.any(poly, 0) == [False, True])
    assert numpy.all(numpy.any(poly, -1, keepdims=True) == [[True], [False]])
