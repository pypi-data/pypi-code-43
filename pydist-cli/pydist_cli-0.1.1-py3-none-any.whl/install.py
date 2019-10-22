import subprocess
import sys


def install(settings, args):
    subprocess.run([
        sys.executable, '-m', 'pip', 'install',
        '--index-url', settings['index'], '--extra-index-url', settings['backup_index'],
        *args,
    ], check=True)
