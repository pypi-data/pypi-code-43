import robotpt_common_utils
import datetime


class TestedSetterAndGetter:
    """
    Stores one Python object.  When that object is set, included tests will be run.
    If `get` is called before the object is assigned, then a ValueError will be raised.

    """
    def __init__(self, value=None, *tests):
        self._is_set = False
        self._last_set = None

        self._tests = []
        self.append_tests(*tests)

        self._value = None
        if value is not None:
            self.set(value)

    def get(self):
        if self._is_set is False:
            raise ValueError("No value set")
        else:
            return self._value

    def get_last_set(self):
        if self.is_set:
            return self._last_set
        else:
            return None

    def set(self, value):
        if self._is_pass_tests(value):
            self._value = value
            self._last_set = datetime.datetime.now()
            self._is_set = True
        else:
            raise ValueError("Must pass all tests to set new value")

    @property
    def is_set(self):
        return self._is_set

    def clear_value(self):
        self._value = None
        self._last_set = None
        self._is_set = False

    def clear_tests(self):
        self._tests = []

    def append_tests(self, *tests):
        if tests is ():
            tests = None
        if tests is not None:
            tests = robotpt_common_utils.lists.make_sure_is_iterable(tests)
            self._tests = robotpt_common_utils.lists.append_to_list(
                self._tests,
                tests,
                callable
            )

    def _is_pass_tests(self, value):
        if len(self._tests) > 0:
            return robotpt_common_utils.lists.is_object_pass_tests(value, *self._tests)
        else:
            return True
