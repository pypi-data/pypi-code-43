import logging
import os

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
if os.environ.get("SETTINGS_LOGGER"):
    logger.setLevel(getattr(logging, os.environ["SETTINGS_LOGGER"]))
    logger.addHandler(logging.StreamHandler())
