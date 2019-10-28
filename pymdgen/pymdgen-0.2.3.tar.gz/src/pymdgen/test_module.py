"""
A module to use as a target during unit tests
"""

from functools import wraps


class prop(object):
    help = "property help"


class dummy(object):
    """
    this is a dummy class

    # Instanced Properties

    - arbitrary property
    - another arbitrary property

    more class docstr
    """

    test_property = prop()

    @classmethod
    def dummy_classmethod(self):
        """ this is a dummy classmethod """

        return

    def dummy_method(self):
        """ this is a dummy func """

        return

    @property
    def dummy_property(self):
        """
        this is a dummy property
        """

        return "dummy"


def dummy_func():
    """ this is a dummy func """
    return

def decorate_this(fn):
    @wraps(fn)
    def wrapped(*args):
        return fn(*args)

    return wrapped

@decorate_this
def decorated_func(specifc):
    """ this is a decorated function """
    return specific


