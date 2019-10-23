"""Resource."""
from typing import Dict, Optional


class TypedResource:

    methods_body_parameters_hints: Dict[str, Optional[str]]
    methods_return_hints: Dict[str, Optional[str]]
