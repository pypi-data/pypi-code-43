import logging

logging.basicConfig(
    datefmt='%Y-%m-%d %H:%M:%S',
    format='[%(asctime)s] %(levelname)s: %(message)s',
    level=logging.INFO
)

def error(msg):
    logging.error(msg)

def info(msg):
    logging.info(msg)

def warning(msg):
    logging.warning(msg)
