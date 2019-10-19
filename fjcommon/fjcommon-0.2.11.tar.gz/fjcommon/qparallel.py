"""
Mimics a small subset of GNU parallel


qparallel --submit "cat bla | qparallel echo {}"

Supported:

Arguemnt substition

Flags
--jobs, -j


"""


import sys


def parallel(args):
    pass


def main(args):
    if '--sub' in args:
        submit(args)
    else:
        parallel(args)


if __name__ == '__main__':
    main(sys.argv[1:])


