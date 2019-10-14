"""
A module to use as a target during unit tests
"""

class prop(object):
    help = "property help"


class dummy(object):
    """ this is a dummy class """

    test_property = prop()

    def dummy_method(self):
        """ this is a dummy func """
        return


def dummy_func():
    """ this is a dummy func """
    return
