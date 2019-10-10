import logging

fmt = "%(levelname)s - %(name)s - %(message)s"
logging.basicConfig(filename="log.log", level=logging.DEBUG, format=fmt)

logger = logging.getLogger("coderadio")
