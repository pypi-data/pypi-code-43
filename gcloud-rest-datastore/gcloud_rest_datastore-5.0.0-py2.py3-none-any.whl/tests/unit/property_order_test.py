from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import str
from future import standard_library
standard_library.install_aliases()
from builtins import object
import pytest
from gcloud.rest.datastore import Direction
from gcloud.rest.datastore import PropertyOrder


class TestPropertyOrder(object):
    @staticmethod
    def test_order_defaults_to_ascending():
        assert PropertyOrder('prop_name').direction == Direction.ASCENDING

    @staticmethod
    def test_order_from_repr(property_order):
        original_order = property_order
        data = {
            'property': {
                'name': original_order.prop
            },
            'direction': original_order.direction
        }

        output_order = PropertyOrder.from_repr(data)

        assert output_order == original_order

    @staticmethod
    def test_order_to_repr():
        property_name = 'my_prop'
        direction = Direction.DESCENDING
        order = PropertyOrder(property_name, direction)

        r = order.to_repr()

        assert r['property']['name'] == property_name
        assert r['direction'] == direction.value

    @staticmethod
    def test_repr_returns_to_repr_as_string(property_order):
        assert repr(property_order) == str(property_order.to_repr())

    @staticmethod
    @pytest.fixture()
    def property_order()                 :
        return PropertyOrder(prop='prop_name', direction=Direction.DESCENDING)
