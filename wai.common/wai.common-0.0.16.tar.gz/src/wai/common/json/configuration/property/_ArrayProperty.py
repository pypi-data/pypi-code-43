from typing import Optional

from ._Property import Property
from ._ProxyProperty import ProxyProperty
from ._ArrayProxy import ArrayProxy


class ArrayProperty(ProxyProperty):
    """
    Property which validates a regular array of elements.
    """
    def __init__(self,
                 sub_property: Property,
                 min_elements: int = 0,
                 max_elements: Optional[int] = None,
                 unique_elements: bool = False):

        # Create a closure class to proxy the array
        class ClosureArrayProxy(ArrayProxy):
            @classmethod
            def sub_property(cls) -> Property:
                return sub_property

            @classmethod
            def min_elements(cls) -> int:
                return min_elements

            @classmethod
            def max_elements(cls) -> Optional[int]:
                return max_elements

            @classmethod
            def unique_elements(cls) -> bool:
                return unique_elements

        super().__init__(
            sub_property.name(),
            ClosureArrayProxy,
            optional=sub_property.is_optional()
        )

    def __set__(self, instance, value):
        # Convert other proxy-arrays and raw lists to our proxy-type
        if (isinstance(value, ArrayProxy) and not isinstance(value, self.type())) or \
           isinstance(value, list):
            value = self.type()(value)

        super().__set__(instance, value)
