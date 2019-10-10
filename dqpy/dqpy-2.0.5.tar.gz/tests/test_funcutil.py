import unittest

from dq.funcutil import safe_invoke


@safe_invoke()
def with_return(name, action=None):
    if action != 'raise':
        return action
    raise Exception


@safe_invoke(noreturn=True)
def no_return(name, action=None):
    if action == 'raise':
        raise Exception
    if action == 'force':
        return 'force'


class TestFuncUtil(unittest.TestCase):

    def test_safe_invoke_success_return(self):
        assert with_return('danqing', action='hi') == 'hi'
        assert with_return('danqing') is None

    def test_safe_invoke_success_noreturn(self):
        assert no_return('danqing', action='hi') is True
        assert no_return('danqing', action='force') is True

    def test_safe_invoke_error_return(self):
        assert with_return('danqing', action='raise') is None

    def test_safe_invoke_error_noreturn(self):
        assert no_return('danqing', action='raise') is None
