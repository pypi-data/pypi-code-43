import re
from lupin.fields import String
from lupin.fields.compatibility import merge_validator
from .validators import IsRegexp


class RegexpField(String):
    """Field storing regexps"""

    def __init__(self, **kwargs):
        merge_validator(kwargs, IsRegexp())
        super().__init__(**kwargs)

    def load(self, value, mapper):
        """Loads a regexp from JSON value

        Args:
            value (string): a pattern string
            mapper (Mapper): mapper used to load data

        Returns:
            object
        """
        if value is not None:
            return re.compile(value)

    def dump(self, value, mapper):
        """Dump a regexp

        Args:
            value (regexp): a value
            mapper (Mapper): mapper used to dump data

        Returns:
            object
        """
        if value is not None:
            return value.pattern
