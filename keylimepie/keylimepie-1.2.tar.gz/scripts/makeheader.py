"""Functions to make a header file suitable for makeLIME.py

Call from the command line:
$ python makeheader.py path/to/file name(optional)
"""

import argparse
import sys
from keylimepie.model.writeheader import make_2d_header


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
    )
    parser.add_argument('filename', help='File to process')
    parser.add_argument(
        '--outfilename', '-o',
        help='Filename for output',
        type=str,
        default=None,
    )
    parser.add_argument(
        '--isotope', '-i',
        help='Fraction of isotope to divide the abundance for, for example, "-i 0.01" for 13C',
        type=float,
        default=1.,
    )
    # parser.add_argument(
    #     '--dust2gas', '-d',
    #     help='Add dust to gas and dust opacity',
    #     type=bool,
    #     default=False,
    # )
    args = parser.parse_args()

    make_2d_header(
        args.filename, args.outfilename, isotope=args.isotope,
        # dust2gas=args.dust2gas
    )
