"""Module for getting information about Python modules."""

import importlib
import typing


def get_module_sources(module_name: str) -> typing.List[str]:
    """Return the list of paths for given Python module.

    Args:
        module_name (str): Name of the Python module.

    Returns:
        :obj:`list` of :obj:`str`: List of source paths for the module.

    """
    module = importlib.__import__(module_name)
    return [f"{module_path}/**/*.py" for module_path in module.__path__]
