"""This is how the major building blocks of the app communicate with each
other. This may be overkill and I may simplify it later, but it is what it is
for now."""

# --- Standard Library Imports ------------------------------------------------
from contextlib import contextmanager

# --- Third Party Imports -----------------------------------------------------
# None

# --- Intra-Package Imports ---------------------------------------------------
from rtm.main.exceptions import UninitializedError


class ContextManager:

    def __init__(self, name):
        """Easily share data amongst all the functions"""
        # TODO This system can and probably should be superseded by something simpler.
        self._name = name
        self._value = None

    @contextmanager
    def set(self, value):
        """Set this object equal to something to make it available to calling functions."""
        self._value = value
        yield
        self._value = None

    def get(self):
        """This is how functions access the values set above."""
        if self._value is None:
            raise UninitializedError(f"The '{self._name}' ContextManager is not initialized")
        else:
            return self._value


worksheet_columns = ContextManager('worksheet_columns')
fields = ContextManager('fields')
work_items = ContextManager('work_items')
