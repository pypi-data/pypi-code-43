''' Print pythonpath

History:
04-09-2018 - 1.0.0 - Stephen Funkhouser
    Created
'''
__version__ = '1.0.0'

import sys

from dds_pylib.util import clear_screen


def print_pythonpath():
    print 'PYTHONPATH:'
    for p in sys.path:
        print p


if __name__ == '__main__':
    clear_screen()
    print_pythonpath()
