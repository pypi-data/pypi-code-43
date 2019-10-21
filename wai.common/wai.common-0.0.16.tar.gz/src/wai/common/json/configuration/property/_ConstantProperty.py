from ..._typing import RawJSONPrimitive
from ...schema import constant
from ._RawProperty import RawProperty


class ConstantProperty(RawProperty):
    """
    Configuration property which validates a constant primitive value.
    """
    def __init__(self,
                 name: str,
                 value: RawJSONPrimitive,
                 *,
                 optional: bool = False):
        super().__init__(
            name,
            constant(value),
            optional=optional
        )
