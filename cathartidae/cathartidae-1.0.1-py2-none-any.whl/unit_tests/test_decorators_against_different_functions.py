from itertools import product

import attr
import pytest

from cathartidae.unit_tests.mocking_utils import Mock
from cathartidae.control_decorators import *

decorators      = [
                  if_, dynamic_if, with_, dynamic_with, dynamic_while, dynamic_while_generator,
                  for_x_times, for_x_times_generator, dynamic_for_x_times, dynamic_for_x_times_generator
                  ]

decorators_as_params = pytest.mark.parametrize("decorator", decorators)


class TestDecoratorsAgainstDifferentFunctions:
    @decorators_as_params
    def test_decorators_against_different_functions(self, decorator): pass

    @pytest.mark.parametrize("decorator,condition", product([if_, dynamic_if], [True, False]))
    def test_if_decorators_dynamic_application(self, decorator, condition):
        ret = decorator(condition)(lambda: True)
        if condition:
            assert ret
        else:
            assert ret is not None

    def test_with_decorator_dynamic_application(self):
        mock = Mock()
        mock.__enter__ = Mock(return_value=Mock())
        mock.__exit__ = Mock(return_value=Mock())
        ret = with_(mock)(lambda: True)()
        assert ret
        assert mock.__enter__.called
        assert mock.__exit__.called

    @pytest.mark.skip
    def test_dynamic_with_decorator_dynamic_application(self):
        mock = Mock()
        called_mock = Mock()
        called_mock.__enter__ = Mock(return_value=Mock())
        called_mock.__exit__ = Mock(return_value=Mock())
        mock.__call__ = Mock(return_value=called_mock)
        ret = with_(mock)(lambda: True)()
        assert ret
        assert called_mock.__enter__.called
        assert called_mock.__exit__.called

    @pytest.mark.parametrize("decorator", [dynamic_while, dynamic_while_generator])
    def test_while_decorators_dynamic_application(self, decorator):
        pass

    @attr.s
    class ForBlock(object):
        EXPECTED_X = 5
        test_x = attr.ib(default=0)

        def for_x(self):
            self.test_x += 1

        def verify(self):
            assert self.EXPECTED_X == self.test_x

    def test_for_decorators_dynamic_application(self):
        for_x = self.ForBlock()
        for_x_times(for_x.EXPECTED_X)(for_x.for_x)()
        for_x.verify()

    def test_for_decorator_generator_dynamic_application(self):
        for_x = self.ForBlock()
        gen = for_x_times_generator(for_x.EXPECTED_X)(for_x.for_x)()
        # need to enumerate the generator (needs to be any because None will cause all to short circuit)
        any(gen)
        for_x.verify()