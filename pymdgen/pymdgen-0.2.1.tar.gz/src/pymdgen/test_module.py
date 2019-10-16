"""
A module to use as a target during unit tests
"""


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
