import os
import sys
from typing import List, Any, Tuple, Dict

IS_PY3 = sys.version_info.major == 3


def getenv(key: str, default: str, ignore_upper: bool = True) -> str:
    _key = key.lower() if ignore_upper else key
    value = os.getenv(_key) or default
    print("\033[033m", f'{_key} ---------------------> {value}', "\033[0m")
    return value


def filter_locals(variables: Dict[str, Any],
                  exclude_keys: Tuple[str, ...] = ('cls',),
                  exclude_val: Tuple[str, ...] = ('',)) -> List[Tuple[str, Any]]:
    return [(k, v) for k, v in variables.items() if v not in exclude_val and k not in exclude_keys]
