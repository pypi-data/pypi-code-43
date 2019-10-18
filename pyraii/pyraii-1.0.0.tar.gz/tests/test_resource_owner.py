from mock_closable import MockClosable
from pyraii.resource_owner import ResourceOwner


class MyResourceOwner(ResourceOwner):
    def __init__(self):
        self.a = MockClosable()
        self.b = MockClosable()
        self.c = MockClosable()


def equals_to(value):
    return lambda x: x == value


def test_owned_resources_closing():
    my_resource_owner = MyResourceOwner()

    def get_close_mask():
        return [
            my_resource_owner.a.times_closed,
            my_resource_owner.b.times_closed,
            my_resource_owner.c.times_closed]

    assert all(map(equals_to(0), get_close_mask()))
    my_resource_owner.close()
    assert all(map(equals_to(1), get_close_mask()))


def test_complex_resource_hierarchy_closing():
    class MyBiggerResourceOwner(ResourceOwner):
        def __init__(self):
            self.x = MyResourceOwner()
            self.y = MockClosable()
            self.z = MyResourceOwner()

    my_resource_owner = MyBiggerResourceOwner()

    def get_close_mask():
        return [
            my_resource_owner.x.a.times_closed,
            my_resource_owner.x.b.times_closed,
            my_resource_owner.x.c.times_closed,
            my_resource_owner.y.times_closed,
            my_resource_owner.x.a.times_closed,
            my_resource_owner.x.b.times_closed,
            my_resource_owner.x.c.times_closed]

    assert all(map(equals_to(0), get_close_mask()))
    my_resource_owner.close()
    assert all(map(equals_to(1), get_close_mask()))
