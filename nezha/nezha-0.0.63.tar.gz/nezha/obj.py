from typing import Tuple


def has_callable_method(obj, method_names: Tuple) -> bool:
    return all(map(lambda name: callable(getattr(obj, name, None)), method_names))
