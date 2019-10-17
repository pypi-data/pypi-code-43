"""The base metric"""

from typing import Optional

class Metric:
    """
    Metric holding the error status.
    """

    def __init__(self, *_args, **_kwargs) -> None:
        self.error: Optional[Exception] = None

    def on_enter(self) -> None:
        """Called at the start of the context"""

    def on_exit(self) -> None:
        """Called at the end of the context"""
