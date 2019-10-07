
from healer.support.typing import *


class BasicEnum(AutoNameEnum):
    NameOne = enum.auto()
    NameTwo = enum.auto()


def test_auto_enum():
    print()
    print(BasicEnum.NameOne)
    print(BasicEnum.NameTwo)
    assert BasicEnum.NameOne == "NameOne"
    assert BasicEnum.NameTwo == "NameTwo"


class SomeUnit(WithLoggerSTD):
    ""


def test_logger_std():
    print()

    some_unit = SomeUnit()

    some_unit.react_stderr("hello")


class DataUnit:
    ""

    @cached_property
    def test_call(self):
        print('hello-kitty')
        return 123


def test_cached_property():
    print()

    data_unit = DataUnit()

    a1 = data_unit.test_call
    a2 = data_unit.test_call
    a3 = data_unit.test_call

    print(a1, a2, a3)


class DataUnitStatic:
    ""

    @staticmethod
    @static_cached_property
    def test_call():
        print('hello-kitty')
        return 123


def test_static_cached_property():
    print()

    a1 = DataUnitStatic.test_call
    a2 = DataUnitStatic.test_call
    a3 = DataUnitStatic.test_call

    print(a1, a2, a3)
