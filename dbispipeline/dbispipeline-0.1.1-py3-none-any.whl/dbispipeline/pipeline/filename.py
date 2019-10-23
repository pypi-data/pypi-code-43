# -*- coding: utf-8 -*-
"""
These transformers can be used if filenames are used as documents.
"""

import os
import pickle
import json

from sklearn.base import BaseEstimator
from sklearn.base import TransformerMixin


class FileReader(BaseEstimator, TransformerMixin):
    """
    Transforms filenames into their content.
    By default, this transformer will open files in text mode.
    This is not a generator, so be careful with your memory.

    input: list of paths
    output: list of contents of the files specified by the paths.
    """

    def __init__(self, mode='text'):
        """
        Args:
            mode: The mode in which the files are to be opened. One of 'text',
                'pickle' or 'json'.
        """
        valid_modes = ['text', 'pickle', 'json']
        if mode not in valid_modes:
            raise ValueError(f'unknown mode {mode}, use one of: {valid_modes}')
        self.mode = mode

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        ret = []
        for document in X:
            if not os.path.isfile(document):
                raise ValueError(f'No such file: {document}')
            if self.mode == 'text':
                with open(document, 'r') as i_f:
                    ret.append(i_f.read())
            elif self.mode == 'json':
                with open(document, 'r') as i_f:
                    ret.append(json.load(i_f))
            if self.mode == 'pickle':
                with open(document, 'rb') as i_f:
                    ret.append(pickle.load(i_f))
        return ret


class FileWriter(BaseEstimator, TransformerMixin):
    """
    Stores elements to filenames, which must be provided at object creation
    time.

    input: list of serializable content
    output: the same content. Storing the files is a side-effect.
    """

    def __init__(self, filenames, writemode='text'):
        """
        Args:
            filenames: one valid path for each entry in X passed to fit()
            writemode: mode in which to write the files. Can be 'text',
                'pickle' or 'pickle'.
        """

        self.filenames = filenames
        valid_writemodes = ['text', 'json', 'pickle']
        if writemode not in valid_writemodes:
            raise ValueError(f'writemode must be one of {valid_writemodes}')
        self.writemode = writemode

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X = list(X)
        assert len(X) == len(self.filenames)
        for i, (filename, document) in enumerate(zip(self.filenames, X)):
            if not os.path.isdir(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename), exist_ok=True)
            if self.writemode == 'text':
                with open(filename, 'w') as o_f:
                    o_f.write(document)
            elif self.writemode == 'json':
                with open(filename, 'w') as o_f:
                    json.dump(document, o_f)
            elif self.writemode == 'pickle':
                with open(filename, 'wb') as o_f:
                    pickle.dump(document, o_f)
        return X


class PathTransformer(TransformerMixin, BaseEstimator):
    """
    Transforms the path of files and allows to replace the extension.

    input: list of paths
    output: list of the same paths that have been modified according to
    the initialization parameters
    """

    def __init__(self, path, extension=None):
        """
        Args:
            path: The path which is appended to each filename
            extension: The new extensions that is used, including the dot.
                This replaces all old extensions: given a file foobar.txt.gz
                and an extension .grammar will result in foobar.grammar.
        """

        self.path = path
        self.extension = extension

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        ret = []
        for x in X:
            base = os.path.dirname(x)
            new_base = os.path.join(base, self.path)
            name = os.path.splitext(os.path.basename(x))[0]
            if self.extension:
                ret.append(os.path.join(new_base, name + self.extension))
            else:
                ret.append(os.path.join(new_base, os.path.basename(x)))
        return ret
