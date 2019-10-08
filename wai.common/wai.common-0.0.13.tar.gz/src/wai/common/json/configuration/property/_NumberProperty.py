from typing import Optional

from ...schema import number
from ..._typing import RawJSONNumber
from ._RawProperty import RawProperty


class NumberProperty(RawProperty):
    """
    Property which validates a number.
    """
    def __init__(self,
                 name: str,
                 minimum: Optional[RawJSONNumber] = None,
                 maximum: Optional[RawJSONNumber] = None,
                 integer_only: bool = False,
                 multiple_of: Optional[RawJSONNumber] = None,
                 exclusive_minimum: bool = False,
                 exclusive_maximum: bool = False,
                 *,
                 optional: bool = False):
        super().__init__(
            name,
            number(
                minimum,
                maximum,
                integer_only,
                multiple_of,
                exclusive_minimum,
                exclusive_maximum
            ),
            optional=optional
        )
