from typing import Optional

from ...schema import string_schema
from ._RawProperty import RawProperty


class StringProperty(RawProperty):
    """
    Configuration property which validates a string.
    """
    def __init__(self,
                 name: str,
                 min_length: Optional[int] = None,
                 max_length: Optional[int] = None,
                 pattern: Optional[str] = None,
                 format: Optional[str] = None,
                 *,
                 optional: bool = False):
        super().__init__(
            name,
            string_schema(
                min_length,
                max_length,
                pattern,
                format
            ),
            optional=optional
        )
