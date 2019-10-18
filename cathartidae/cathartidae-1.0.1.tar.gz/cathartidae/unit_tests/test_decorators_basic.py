import pytest
from itertools import product
from threading import Lock

from cathartidae.control_decorators import *
from cathartidae.unit_tests.basic_decorated_test_methods import BasicDecoratedTestMethods

invalid_methods = [
                    if_(True), dynamic_if(lambda: True), with_(Lock()),  dynamic_with(lambda: Lock()),
                    dynamic_while(lambda: True), dynamic_while_generator(lambda: True),
                    for_x_times(5), for_x_times_generator(5), dynamic_for_x_times(lambda: 5),
                    dynamic_for_x_times_generator(lambda: 5)
                  ]

class TestDecoratorsBasic(object):
    def test_if_decorator(self):
        try:
            BasicDecoratedTestMethods.if_test_true()
        except:
            pass
        else:
            pytest.fail("did not pass through if logic")

        try:
            BasicDecoratedTestMethods.if_test_false()
        except:
            pytest.xfail("still called if decorated")

    def test_with_decorator(self):
        BasicDecoratedTestMethods.with_test()

    def test_dynamic_while_decorator(self):
        BasicDecoratedTestMethods.dynamic_while_test()

    def test_for_decorator(self):
        BasicDecoratedTestMethods.for_test()

    @pytest.mark.parametrize("control_decorator,invalid_method", product(invalid_methods, [staticmethod, classmethod]))
    def test_invalid_method_wrapped_as_inner_function_raises_exception(self, control_decorator, invalid_method):
        try:
            # static application
            class A:
                @control_decorator
                @invalid_method
                def x(self): pass

            pytest.fail("no exception was raised")
        except ValueError: pass
        except Exception as e:
            import pdb; pdb.set_trace()
            pytest.fail("wrong exception was raised")

        try:
            control_decorator(invalid_method(lambda: 6))
            pytest.fail("no exception was raised")
        except ValueError: pass
        except:
            pytest.fail("wrong exception was raised")