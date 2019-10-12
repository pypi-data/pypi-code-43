__version__ = '5.0.7'

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from dataclasses import dataclass

    # noinspection PyUnresolvedReferences
    from typing import Generic

    raise Exception()
else:
    # noinspection PyUnresolvedReferences
    from .monkey_patching_typing import my_dataclass as dataclass

    # noinspection PyUnresolvedReferences
    from .monkey_patching_typing import ZenericFix as Generic

from .debug_print_ import debug_print
