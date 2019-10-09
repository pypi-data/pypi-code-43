import importlib

from coderadio.core.log import logger


def load_plugin(path_to_plugin):
    try:
        plug = importlib.import_module(path_to_plugin)
        return plug
    except ImportError as exc:
        logger.debug(exc)
