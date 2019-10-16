import shutil
from .exceptions import GeofilesError, LoadingError, ReadingError


def test_wgrib():
    success = True
    if not shutil.which('wgrib'):
        success = False
        print('wgrib not installed')
    if not shutil.which('wgrib2'):
        success = False
        print('wgrib2 not installed')
    if success:
        print('Everything installed')


# Make submodules available when just importing the top-level package
from . import conversion
from . import datasets
from . import loading
from . import reading
from . import writing
