''' Clear screen

History:
06-11-2016 - 1.0.0 - Stephen Funkhouser
    Created
'''
__version__ = '1.0.0'

import sys


def clear_screen():
    sys.stderr.write("\x1b[2J\x1b[H")


if __name__ == '__main__':
    clear_screen()
