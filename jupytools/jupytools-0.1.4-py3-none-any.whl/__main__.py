import argparse
import os
import sys

from jupytools.export import to_py


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', dest='root', default=os.getcwd(),
        help='root directory to export notebooks from'
    )
    parser.add_argument(
        '-nb', default=None,
        help='if provided, then only a single notebook will be exported',
    )
    parser.add_argument(
        '-e', dest='except', default=None, nargs='*',
        help='notebooks to exclude from export'
    )
    parser.add_argument(
        '-o', dest='out', default='exported',
        help='folder to save exported .py files'
    )
    parser.add_argument(
        '-gap', type=int, default=3,
        help='number of empty lines between exported cells'
    )
    parser.add_argument(
        '-asis', action='store_true',
        help='if provided, then script doesn\'t try to strip notebooks names '
             'to exclude numerical prefixes.'
    )
    args = vars(parser.parse_args())
    to_py(source_dir=args['root'], nb_name=args['nb'],
          output_dir=args['out'], gap=args['gap'],
          keep_names=args['asis'])


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == 'export':
        sys.argv = sys.argv[1:]
        main()
