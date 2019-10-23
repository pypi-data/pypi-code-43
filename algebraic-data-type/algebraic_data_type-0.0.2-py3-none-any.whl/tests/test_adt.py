from ..adt import ADTMeta, Multimethod, Case, T, _

class Optional(metaclass=ADTMeta):
    Just: Case(x=T)
    Empty: Case()

with Multimethod() as inverse:
    inverse[Optional.Just(_)] = lambda x: Optional.Just(1/x)
    inverse[Optional.Empty()] = Optional.Empty()

def test_matching():
    assert inverse(Optional.Just(2)) == Optional.Just(0.5)
    assert inverse(Optional.Empty()) == Optional.Empty()


