from enum import Enum, IntEnum
import pytest

from azureml.studio.common.types import get_enum_values
from azureml.studio.modulehost.attributes import ItemInfo, AutoEnum


class E1(AutoEnum):
    A = ()
    B = ()


class E2(Enum):
    A = 1
    B = 2


class E3(IntEnum):
    A = 1
    B = 2


class E4(AutoEnum):
    A: ItemInfo(name="E4_A", friendly_name="AAA") = ()
    B: ItemInfo(name="E4_B", friendly_name="BBB") = ()
    '''
    name conflicts
    '''
    C: ItemInfo(name="D", friendly_name="CCC") = ()
    D = ()
    '''
    custom function
    '''
    def F(self):
        pass


def test_enum_parsing_basic():
    assert ItemInfo.get_enum_value_by_name(E1, 'A') == E1.A
    assert ItemInfo.get_enum_value_by_name(E1, 'B') == E1.B
    assert ItemInfo.get_enum_value_by_name(E2, 'A') == E2.A
    assert ItemInfo.get_enum_value_by_name(E2, 'B') == E2.B
    assert ItemInfo.get_enum_value_by_name(E3, 'A') == E3.A
    assert ItemInfo.get_enum_value_by_name(E3, 'B') == E3.B


def test_enum_parsing_by_item_info():
    assert ItemInfo.get_enum_value_by_name(E4, 'E4_A') == E4.A
    assert ItemInfo.get_enum_value_by_name(E4, 'E4_B') == E4.B
    assert ItemInfo.get_enum_value_by_name(E4, 'C') == E4.C
    assert ItemInfo.get_enum_value_by_name(E4, 'D') == E4.C  # not wrong for this

    with pytest.raises(ValueError):
        ItemInfo.get_enum_value_by_name(E4, 'F')


def test_enum_get_values():
    assert [E1.A, E1.B] == get_enum_values(E1)
    assert [E2.A, E2.B] == get_enum_values(E2)
    assert [E3.A, E3.B] == get_enum_values(E3)
    assert [E4.A, E4.B, E4.C, E4.D] == get_enum_values(E4)


def test_get_friendly_name():
    assert ['AAA', 'BBB', 'CCC', 'D'] == [ItemInfo.get_enum_friendly_name(e) for e in get_enum_values(E4)]
