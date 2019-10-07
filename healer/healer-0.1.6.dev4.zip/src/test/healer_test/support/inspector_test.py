
from healer.support.inspector import *


class MateBase(object):

    attribute = "attribute"

    def regular_method(self):
        return "regular_method"

    @property
    def property_method(self):
        return "property_method"

    @classmethod
    def class_method(cls):
        return "class_method"

    @staticmethod
    def static_method():
        return "static_method"


class MateCore(MateBase):
    pass


def test_type_detect():

    assert is_attribute(MateCore, "attribute", MateCore.attribute)

    assert is_property_method(
        MateCore, "property_method", MateCore.property_method)

    assert is_regular_method(
        MateCore, "regular_method", MateCore.regular_method)

    assert is_static_method(
        MateCore, "static_method", MateCore.static_method)

    assert is_class_method(MateCore, "class_method", MateCore.class_method)

    attr_list = [
        (MateCore, "attribute", MateCore.attribute),
        (MateCore, "property_method", MateCore.property_method),
        (MateCore, "regular_method", MateCore.regular_method),
        (MateCore, "static_method", MateCore.static_method),
        (MateCore, "class_method", MateCore.class_method),
    ]

    checker_list = [
        is_attribute,
        is_property_method,
        is_regular_method,
        is_static_method,
        is_class_method,
    ]

    for one, pair in enumerate(attr_list):
        klass, attr, value = pair
        for two, checker in enumerate(checker_list):
            if one == two:
                assert checker(klass, attr, value) is True
            else:
                assert checker(klass, attr, value) is False


def test_getter():

    def items_to_keys(items):
        return set([item[0] for item in items])

    assert items_to_keys(get_attributes(MateCore)) == {"attribute"}

    assert items_to_keys(
        get_property_methods(MateCore)) == {"property_method"}

    assert items_to_keys(
        get_regular_methods(MateCore)) == {"regular_method"}

    assert items_to_keys(
        get_static_methods(MateCore)) == {"static_method"}

    assert items_to_keys(
        get_class_methods(MateCore)) == {"class_method"}

    assert items_to_keys(
        get_all_attributes(MateCore)) == {"attribute", "property_method"}

    assert items_to_keys(
        get_all_methods(MateCore)) == {"regular_method", "static_method", "class_method"}

