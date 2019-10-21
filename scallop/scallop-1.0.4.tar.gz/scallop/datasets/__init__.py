from .joost2016 import joost2016

import os

def delete_datasets(name = None):
    """
    Deletes all downloaded datasets.

    Parameters
    ----------
    name: ``str``
        Substring or string of dataset to remove ('joost2016').
    """
    dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'
    del_formats = ['h5ad', 'txt', 'mtx', 'csv', 'zip', 'tar', 'gz', 'rar']

    for file in os.listdir(dir_path):
        for del_fmt in del_formats:
            if file.endswith(del_fmt):
                if name is None:
                    print('Deleting {file}'.format(file=file))
                    os.remove(dir_path + '/' + file)
                else:
                    if file.__contains__(name):
                        print('Deleting {file}'.format(file=file))
                        os.remove(dir_path + '/' + file)