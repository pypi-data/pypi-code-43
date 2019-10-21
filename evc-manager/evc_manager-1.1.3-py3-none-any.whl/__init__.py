import logging
from logging import NullHandler
from .evc_manager import EvcManager


evc_manager = EvcManager()

# Set default logging handler to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(NullHandler())
