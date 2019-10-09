import logging
import subprocess
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


logger = logging.getLogger(__name__)


def detect_git_info():
    try:
        info = {
            'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip(),
            'root': subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).decode('utf-8').strip(),
            'repository': subprocess.check_output(['git', 'remote', 'get-url', 'origin']).decode('utf-8').strip(),
            'branch': subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('utf-8').strip(),
        }
        logger.debug("autodetected git info: %s", info)
        return info
    except (FileNotFoundError, subprocess.CalledProcessError,):
        logger.debug("couldn't autodetect git information", exc_info=True)
        return {}
