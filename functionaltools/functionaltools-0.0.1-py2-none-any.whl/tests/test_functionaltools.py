import pytest
from functionaltools.functionaltools import *


@pytest.fixture
def list_a():
    return [0, 1, 2, 3, 4]


@pytest.fixture
def list_b():
    return [5, 6, 7, 8, 9]
    

@pytest.fixture
def props():
    return {"name": "Bob",
            "age": 30}


class Test_Reduce:
    def test_reducer(self, list_a):
        reducer = lambda x, y: x+y
        add = reduce(reducer)
        assert add(list_a) == 10

    def test_with_initial(self, list_a):
        """Should start with 1."""
        reducer = lambda x, y: x+y
        add = reduce(reducer, init=1)
        assert add(list_a) == 11
    

def test_ifElse(props):
    onTrue = ifElse(lambda _: True, prop("name"), prop("age"))
    onFalse = ifElse(lambda _: False, prop("name"), prop("age"))
    assert onTrue(props) == "Bob"
    assert onFalse(props) == 30


def test_prop(props):
    first = prop("name")
    last = prop("age")
    assert first(props) == "Bob"
    assert last(props) == 30


def test_equals():
    test = equals(True)
    assert test(True) == True
    assert test(False) == False


def test_notEquals():
    test = notEquals(True)
    assert test(True) == False
    assert test(False) == True


def test_all():
    results = all(equals(True))
    assert results([True, False]) == False
    assert results([False, False]) == False
    assert results([True, True]) == True
    
    
def test_reduce():
    add = pipe(
        reduce(lambda x, y: x+y)
    )
    results = add([1,2,3])
    assert results == 6


def test_elem():
    a = "hello world"
    b = "hellow if true world"
    hasIfTrue = elem("if true")
    assert hasIfTrue(a) == False
    assert hasIfTrue(b) == True

class Test_Fork:
    def test_fork(self):
        results = fork(([],[]), lambda x: x == True, [True,False,False])
        assert results == ([True],[False,False])
