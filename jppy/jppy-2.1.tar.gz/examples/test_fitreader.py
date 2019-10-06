#!/usr/bin/env python
"""
Test the fitreader. This Plots the Z-dir of the first JFit given by JEvt.
By Giuliano + Moritz.

Usage:
    test_fitreader.py [-p PLOTFILE] INFILE

Options:
    -p PLOTFILE         Name of the pdf file [default: test_fitreader.pdf]
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def read_fits(fname):
    from jppy.fitreader import PyJFitReader

    fr = PyJFitReader(fname)
    dirs_z = []

    while fr.has_next:
        fr.retrieve_next_event()
        n_fits = fr.n_fits

        if n_fits == 0:
            continue

        buf_size = 500000
        pos_xs = np.zeros(buf_size, dtype='d')
        pos_ys = np.zeros(buf_size, dtype='d')
        pos_zs = np.zeros(buf_size, dtype='d')
        dir_xs = np.zeros(buf_size, dtype='d')
        dir_ys = np.zeros(buf_size, dtype='d')
        dir_zs = np.zeros(buf_size, dtype='d')
        ndfs = np.zeros(buf_size, dtype='i')
        times = np.zeros(buf_size, dtype='d')
        qualities = np.zeros(buf_size, dtype='d')
        energies = np.zeros(buf_size, dtype='d')

        fr.get_fits(
            pos_xs,
            pos_ys,
            pos_zs,
            dir_xs,
            dir_ys,
            dir_zs,
            ndfs,
            times,
            qualities,
            energies,
        )

        dirs_z.append(dir_zs[0])

    return dirs_z


if __name__ == '__main__':
    from docopt import docopt
    args = docopt(__doc__)
    infile = args['INFILE']
    plotfile = args['-p']

    dirs_z = read_fits(infile)
    dirs_z = pd.Series(dirs_z)

    entries = len(dirs_z)
    mean = sum(dirs_z) / entries

    plt.clf()
    plt.hist(dirs_z, bins=50, range=[-1., 1.], linewidth=2, histtype='step',
             label=' Entries ' + str(entries) + '\n Mean: ' + str(mean)[0:5])
    plt.figtext(1.0, 0.2, dirs_z.describe())
    plt.xlabel('Z-Dir of first JFit in JEvt', size=12)
    plt.grid()
    plt.legend(bbox_to_anchor=(0.3, 0.9), ncol=1, loc='best')
    # plt.show()
    plt.savefig(plotfile)
    plt.close()
