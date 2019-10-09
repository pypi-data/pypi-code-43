from ._Property import Property
from ._ProxyProperty import ProxyProperty
from ._MapProxy import MapProxy


class MapProperty(ProxyProperty):
    """
    Property which validates a map of strings to some other type.
    """
    def __init__(self,
                 sub_property: Property):

        # Create a closure class to proxy the array
        class ClosureMapProxy(MapProxy):
            @classmethod
            def sub_property(cls) -> Property:
                return sub_property

        super().__init__(
            sub_property.name(),
            ClosureMapProxy,
            optional=sub_property.is_optional()
        )

    def __set__(self, instance, value):
        # Convert other proxy-maps and raw dicts to our proxy-type
        if (isinstance(value, MapProxy) and not isinstance(value, self.type())) or \
           isinstance(value, dict):
            value = self.type()(value)

        super().__set__(instance, value)
