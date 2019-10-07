
import logging

from healer.config import *

logger = logging.getLogger(__name__)


def test_config():
    print()
    
    logger.trace(f"trace level")

    print(CONFIG)
