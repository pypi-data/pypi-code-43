import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from ucamdsm.lib.options import Options

LOG = logging.getLogger(__name__)

LOG_DIR = '/var/log/ucamdsm'
LOG_FILE = 'ucamdsm.log'
ROTATING_FILE_HANDLER_MAXBYTES = 10 * 1000 * 1000  # 10 mbytes
ROTATING_FILE_HANDLER_BACKUPCOUNT = 5

Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

stdout_handler = logging.StreamHandler(sys.stdout)
file_handler = RotatingFileHandler(filename=f'{LOG_DIR}/{LOG_FILE}',
                                   maxBytes=ROTATING_FILE_HANDLER_MAXBYTES,
                                   backupCount=ROTATING_FILE_HANDLER_BACKUPCOUNT)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    handlers=[file_handler, stdout_handler])


def run_project(args):
    options = Options()
    return options.parse(args[1:])


def main():
    result = False
    try:
        result = run_project(sys.argv)
    except KeyboardInterrupt:
        sys.exit()
    except Exception as error:
        LOG.error('Please check your command input. %s', error)
        sys.exit()

    if result:
        LOG.info('[Command succeeded - Returns %s]', result)
    else:
        LOG.error('[Command failed - Returns %s]', result)

    return result


if __name__ == '__main__':
    main()
