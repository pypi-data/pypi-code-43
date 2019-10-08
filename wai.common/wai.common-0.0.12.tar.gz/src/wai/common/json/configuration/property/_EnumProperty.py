from ..._typing import RawJSONPrimitive
from ...schema import enum
from ._RawProperty import RawProperty


class EnumProperty(RawProperty):
    """
    Property which accepts one of a set of specific primitive values.
    """
    def __init__(self,
                 name: str,
                 *values: RawJSONPrimitive,
                 optional: bool = False):
        super().__init__(
            name,
            enum(*values),
            optional=optional
        )
