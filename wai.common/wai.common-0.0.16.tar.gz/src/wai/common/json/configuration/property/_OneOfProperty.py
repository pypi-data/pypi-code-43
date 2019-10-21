from typing import List, Optional

from ...schema import one_of
from ._OfProperty import OfProperty
from ._Property import Property
from ._DummyInstance import DummyInstance


class OneOfProperty(OfProperty):
    """
    Property which validates JSON that matches exactly one of
    a number of schema.
    """
    def __init__(self,
                 name: str,
                 *sub_properties: Property,
                 optional: bool = False):
        super().__init__(
            name,
            *sub_properties,
            schema_function=one_of,
            optional=optional
        )

    def choose_current_property(self, keys: List[Optional[DummyInstance]]) -> int:
        # Start with an invalid index
        index = -1

        # Search the list
        for i, key in enumerate(keys):
            if key is not None:
                if index >= 0:
                    raise AttributeError(f"Value matched more than one sub-property")

                index = i

        if index == -1:
            raise AttributeError(f"Value didn't match any sub-properties")

        return index
