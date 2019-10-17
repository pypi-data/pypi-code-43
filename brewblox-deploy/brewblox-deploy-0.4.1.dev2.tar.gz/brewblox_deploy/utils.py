"""
Utility functions
"""

from distutils.util import strtobool


def confirm(question):
    print('{} [Y/n]'.format(question))
    while True:
        try:
            return bool(strtobool(input().lower() or 'y'))
        except ValueError:
            print('Please respond with \'y(es)\' or \'n(o)\'.')
