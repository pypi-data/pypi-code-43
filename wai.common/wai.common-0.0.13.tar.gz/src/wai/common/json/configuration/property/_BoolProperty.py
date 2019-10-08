from ...schema import BOOL_SCHEMA
from ._RawProperty import RawProperty


class BoolProperty(RawProperty):
    """
    Configuration property which validates a boolean value.
    """
    def __init__(self,
                 name: str,
                 *,
                 optional: bool = False):
        super().__init__(
            name,
            BOOL_SCHEMA,
            optional=optional
        )
