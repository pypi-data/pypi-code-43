from typing import List, Optional

from ...schema import any_of
from ._OfProperty import OfProperty
from ._Property import Property
from ._DummyInstance import DummyInstance


class AnyOfProperty(OfProperty):
    """
    Property which validates JSON that matches at least one of
    a number of schema.
    """
    def __init__(self,
                 name: str,
                 *sub_properties: Property,
                 optional: bool = False):
        super().__init__(
            name,
            *sub_properties,
            schema_function=any_of,
            optional=optional
        )

    def choose_current_property(self, keys: List[Optional[DummyInstance]]) -> int:
        # Search the list
        for i, key in enumerate(keys):
            # Return the first valid index found
            if key is not None:
                return i

        raise AttributeError(f"Value didn't match any sub-properties")
