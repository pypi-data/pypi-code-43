VERSION_MAJOR = 0  # (System version)
VERSION_MINOR = 0  # (Tests version)
BUILD_NUMBER = 18   # (Issues version)
SNAPSHOT_NUMBER = 0

__version__ = '.'.join(map(str, (VERSION_MAJOR, VERSION_MINOR, BUILD_NUMBER))) if SNAPSHOT_NUMBER == 0 \
    else '.'.join(map(str, (VERSION_MAJOR, VERSION_MINOR, BUILD_NUMBER, 'snapshot.{}'.format(SNAPSHOT_NUMBER))))
__copyright__ = "(c) 2019 Alphaopen LLC | www.alphaopen.com"