import logging
import os

from importlib_metadata import PackageNotFoundError, version

try:
    level = getattr(logging, os.environ["RYE_LOG_LEVEL"])
except (AttributeError, KeyError):
    level = logging.WARNING


logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
try:
    __version__ = version("rye")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
