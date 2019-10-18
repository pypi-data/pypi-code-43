from mock_closable import MockClosable
from pyraii.resource_list import ResourcesList


def test_resource_list_close_order():
    a = MockClosable()
    b = MockClosable()
    c = MockClosable()
    my_list = ResourcesList(a, b, c)
    my_list.close()
    assert all([x.is_properly_closed for x in my_list.resources])
    assert a.relative_close_order > b.relative_close_order > c.relative_close_order


def test_iter():
    a = MockClosable()
    b = MockClosable()
    c = MockClosable()
    for x, y in zip(ResourcesList(a, b, c), [a, b, c]):
        assert x == y
