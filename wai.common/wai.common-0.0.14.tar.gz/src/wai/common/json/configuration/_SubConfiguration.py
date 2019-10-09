from typing import Type

from .property import ProxyProperty
from ._Configuration import Configuration


class SubConfiguration(ProxyProperty):
    """
    Property which validates a sub-configuration (essentially an object).
    """
    def __init__(self,
                 name: str,
                 configuration_type: Type[Configuration],
                 *,
                 optional: bool = False):
        super().__init__(
            name,
            configuration_type,
            optional=optional
        )
