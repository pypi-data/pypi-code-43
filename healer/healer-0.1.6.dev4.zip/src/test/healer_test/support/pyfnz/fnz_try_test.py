
from healer.support.pyfnz import *


def test_try():
    print()
    print(Try(lambda : "x"))
    print(Try(lambda x: x, "x"))
    print(Try(lambda : (_ for _ in ()).throw(RuntimeError("x"))))
