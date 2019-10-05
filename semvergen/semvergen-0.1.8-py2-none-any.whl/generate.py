import re
import subprocess
import sys


def _get_latest_tag():
    out = subprocess.Popen(['git', 'describe', '--tags', '--always'],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)

    stdout, stderr = out.communicate()

    if stderr:
        print(stderr)
        sys.exit(1)

    return stdout.decode('utf-8').strip()


def version():
    version = _get_latest_tag()

    if '-' not in version:
        return version

    major_minor = re.match(r'\d+\.\d+\.', version)
    patch = re.search(r'-(\d+)-', version)

    if not patch or not major_minor:
        return 'Version is wrong. %s' % version

    return '%s%s' % (major_minor.group(), patch.group(1))


if __name__ == '__main__':
    print(version())
