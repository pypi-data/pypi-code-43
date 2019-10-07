
from healer.support.parser import *


def test_convert_camel_under():
    print()

    assert convert_camel_under('HelloKittyABC') == "hello_kitty_abc"
