import sys

from loguru import logger

# For scripts
config = {
    "handlers": [
        {"sink": sys.stdout, "format": "[{time}] | {level} | <level>{message}</level>"},
        {"sink": "file.log", "serialize": False},
    ]
}
logger.configure(**config)

# For libraries
logger.disable("my_library")
logger.info("No matter added sinks, this message is not displayed")
logger.enable("my_library")
logger.info("This message however is propagated to the sinks")