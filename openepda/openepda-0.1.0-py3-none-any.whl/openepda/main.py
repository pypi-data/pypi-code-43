# coding: utf-8
import collections.abc as coll
from csv import QUOTE_NONNUMERIC
from datetime import datetime
import os

import numpy as np
from ruamel.yaml import YAML
import pandas as pd
from pandas.errors import ParserError


def is_list_or_tuple(x):
    """ Check if a variable is either a tuple or a list

    Returns
    -------
    bool
        True if x is a tuple or list, or a subclass of these; False otherwise

    Examples
    --------
    >>> i = 1; f = 1.1; st = 's'; bs = b'S'
    >>> d = {1: 1, 2: 2}; s = {1, 2, 3}
    >>> l = [1, 2]; t = (1, 2)
    >>> arr = np.asarray([1, 2, 3]); m = np.matrix([1, 2, 3])
    >>> is_list_or_tuple(i), is_list_or_tuple(f)
    (False, False)
    >>> is_list_or_tuple(st), is_list_or_tuple(bs)
    (False, False)
    >>> is_list_or_tuple(d), is_list_or_tuple(s)
    (False, False)
    >>> is_list_or_tuple(l), is_list_or_tuple(t)
    (True, True)
    >>> is_list_or_tuple(arr), is_list_or_tuple(m)
    (False, False)
    """

    is_sequence = isinstance(x, coll.Sequence)
    is_str = isinstance(x, (str, coll.ByteString))
    return is_sequence and not is_str


def is_array_like(x):
    """ Check if a variable is array-like

    Returns
    -------
    bool
        True if x is a tuple, a list, a numpy.ndarray, or a subclass of these;
        False otherwise

    Examples
    --------
    >>> i = 1; f = 1.1; st = 's'; bs = b'S'
    >>> d = {1: 1, 2: 2}; s = {1, 2, 3}
    >>> l = [1, 2]; t = (1, 2)
    >>> arr = np.asarray([1, 2, 3]); m = np.matrix([1, 2, 3])
    >>> is_array_like(i), is_array_like(f)
    (False, False)
    >>> is_array_like(st), is_array_like(bs)
    (False, False)
    >>> is_array_like(d), is_array_like(s)
    (False, False)
    >>> is_array_like(l), is_array_like(t)
    (True, True)
    >>> is_array_like(arr), is_array_like(m)
    (True, True)
    """
    x_is_list_or_tuple = is_list_or_tuple(x)
    is_ndarray = isinstance(x, np.ndarray)
    return x_is_list_or_tuple or is_ndarray


class OpenEpdaDataLoader(object):

    def __init__(self):
        super().__init__()

    def read_file(self, fname):

        with open(fname, 'r') as f:

            lines = []
            separator_index = 0
            for i, line in enumerate(f):
                if line != '---\n':
                    lines.append(line)
                else:
                    separator_index = i
                    break

        if separator_index == 0:
            raise ValueError('File "{}" does not confirm to the OpenEpda ' 
                             'Data format: "---" line is missing. File will '
                             'be skipped.'.format(os.path.basename(fname)))

        yaml = YAML(typ='safe')
        yaml.default_flow_style = False
        yaml.explicit_end = None

        data = '\n'.join(lines)
        file_data = yaml.load(data)

        try:
            data = pd.read_csv(fname, header=separator_index + 1)

            for col_name in data.columns:
                file_data.update({col_name: data[col_name].values})
        except ParserError:
            pass

        return file_data


def split_array_data(data, how='max_length'):
    """

    Parameters
    ----------
    how : str
        'max_length|most_common'

    Examples
    --------
    >>> split_array_data({2: [1, 2], '2a': [1, 4]})
    ({}, {2: [1, 2], '2a': [1, 4]})

    >>> split_array_data({2: [1, 2], 3: [1, 2, 3], '3a': [1, 2, 4]})
    ({2: [1, 2]}, {3: [1, 2, 3], '3a': [1, 2, 4]})

    >>> split_array_data({2: [1, 2, 3], 3: [1, 2], '3a': [1, 2]}, how='most_common')
    ({2: [1, 2, 3]}, {3: [1, 2], '3a': [1, 2]})
    """
    if len(data) == 0:
        return data, {}

    lengths = list(map(len, data.values()))

    if how == 'max_length':
        l_csv = max(lengths)
    elif how == 'most_common':
        l_csv = max(set(lengths), key=lengths.count)
    else:
        raise ValueError('Unknown value for how: {}'.format(how))

    csv_data = {}
    meta_data = {}

    for k, v in data.items():
        if len(v) == l_csv:
            csv_data.update({k: v})
        else:
            meta_data.update({k: v})

    return meta_data, csv_data


class OpenEpdaDataDumper(object):

    def __init__(self, csv_data='max_length', float_format=None):
        super().__init__()
        self._csv_data = csv_data
        self._float_format = float_format

    def write(self, stream,  **data):
        """
        Parameters
        ----------
        stream : Any

        data : dict

        """
        yaml_data = {'_timestamp': datetime.now().isoformat()}
        array_data = {}

        for k, v in data.items():
            if is_array_like(v):
                try:
                    l = v.tolist()
                except:
                    l = list(v)
                array_data.update({k: l})
            else:
                yaml_data.update({k: v})

        meta_data, csv_data_dict = split_array_data(array_data,
                                                    how=self._csv_data)
        yaml_data.update(meta_data)

        # csv_data = np.array(list(csv_data_dict.values())).T
        # csv_data_keys = list(csv_data_dict.keys())

        # self._l.debug('yaml keys: {}'.format(yaml_data.keys()))
        # self._l.debug('yaml type: {}'.format(type(yaml_data)))
        # self._l.debug('csv keys: {}, shape: {}'.format(csv_data_keys,
        #                                                csv_data.shape))

        stream.write('# OpenEPDA DATA FORMAT v.0.1\n')

        yaml = YAML()
        yaml.default_flow_style = False
        yaml.explicit_end = None
        yaml.dump(yaml_data, stream)

        stream.write('---\n')

        df_csv = pd.DataFrame(csv_data_dict)
        # np.savetxt(stream, csv_data, delimiter=',',
        #            header=','.join(['"{}"'.format(k) for k in csv_data_keys]),
        #            comments='', fmt=self._float_format)
        df_csv.to_csv(stream, sep=',', quoting=QUOTE_NONNUMERIC,
                      decimal='.', index=False,
                      float_format=self._float_format)
