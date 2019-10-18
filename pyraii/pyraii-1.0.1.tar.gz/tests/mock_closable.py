_g_close_order = 0


class MockClosable(object):
    """
    Mocks a python object which has a closing behaviour
    Can be closed multiple times.
    """

    def __init__(self, exception_on_close=None):
        self._times_closed = 0
        self.exception_on_close = exception_on_close
        self._relative_close_order = None

    def close(self):
        self._times_closed += 1
        if not self._relative_close_order:
            global _g_close_order
            self._relative_close_order = _g_close_order
            _g_close_order += 1
        if self.exception_on_close:
            raise self.exception_on_close

    @property
    def is_closed(self):
        """
        :return: True if was closed at-least one time, False otherwise
        :rtype: bool
        """
        return self._times_closed > 0

    @property
    def times_closed(self):
        """
        :return: Number of times this object was closed
        :rtype: int
        """
        return self._times_closed

    @property
    def is_properly_closed(self):
        """
        :return: True if is closed and was closed once
        """
        return self.is_closed and self.times_closed == 1

    @property
    def relative_close_order(self):
        """
        .. code-block:: python
            a = MockClosable()
            b = MockClosable()
            a.close()
            b.close()
            assert a.relative_close_order < b.relative_close_order
        """
        return self._relative_close_order
