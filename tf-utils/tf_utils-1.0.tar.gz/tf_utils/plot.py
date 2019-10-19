import matplotlib
import numpy as np

import matplotlib.pyplot as plt

import collections
import pickle
import os


class ImagePlot:
    """
    Draws a graph of changing value
    """
    def __init__(self):
        matplotlib.use('Agg')

        self._since_beginning = collections.defaultdict(lambda: {})
        self._since_last_flush = collections.defaultdict(lambda: {})

        self._iter = [0]

    def tick(self):
        self._iter[0] += 1

    def get_tick(self):
        return self._iter[0]

    def plot(self, name, value):
        self._since_last_flush[name][self._iter[0]] = value

    def flush(self, data_dir):
        prints = []
        data_dir = data_dir + '/loss_plot/'
        os.makedirs(os.path.dirname(data_dir), exist_ok=True)
        for name, vals in self._since_last_flush.items():
            val = np.array(list(vals.values())).mean()
            prints.append("{}\t{}".format(name, val))
            self._since_beginning[name].update(vals)

            keys = np.array(list(self._since_beginning[name].keys()))
            x_vals = np.sort(keys)
            y_vals = [self._since_beginning[name][x] for x in x_vals]

            plt.clf()
            plt.plot(x_vals, y_vals)
            plt.xlabel('iteration')
            plt.ylabel(name)
            plt.savefig(data_dir + name.replace(' ', '_') + '.jpg')

        print("iter {}\t{}".format(self._iter[0], "\t".join(prints)))
        self._since_last_flush.clear()

        with open(data_dir + 'log.pkl', 'wb') as f:
            pickle.dump(dict(self._since_beginning), f, pickle.HIGHEST_PROTOCOL)
        plt.clf()
