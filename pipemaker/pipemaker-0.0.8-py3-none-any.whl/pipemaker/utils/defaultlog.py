import logging
from logging import StreamHandler, Formatter, getLogger

# file/line locates source
fmt = Formatter(fmt='[%(name)s:%(levelname)s]:%(message)s (%(filename)s:%(lineno)s, time=%(asctime)s)',
                datefmt='%b-%d %H:%M')

# stream
stream = StreamHandler()
stream.setFormatter(fmt)

# rabbit
from .rabbithandler import RabbitHandler
rabbit = RabbitHandler()
rabbit.setFormatter(fmt)

# prevent imported package verbosity
for name in ["pika", "werkzeug"]:
    getLogger(name).setLevel(logging.WARNING)

# package level
log = getLogger()
log.handlers = [stream, rabbit]
log.setLevel(logging.INFO)

################################################################
#from logging.handlers import RotatingFileHandler
#from pythonjsonlogger import jsonlogger
#fmt_json = jsonlogger.JsonFormatter(reserved_attrs=[])
# rotating = RotatingFileHandler()
# rotating.setFormatter(fmt_simple, filename=log.txt, maxBytes=10000000, backupCount=10, encoding="utf8")

