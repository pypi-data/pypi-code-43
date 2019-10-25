# -*- coding: utf-8 -*-
"""
CSV file reader and writer

With this class, you can read a text file or write a new one with your own
dataset (Pandas Dataframe).

Examples:

    * Read an existing file

    >>> exch = Csv(os.path.join('maplearn path', 'datasets', 'ex1.xlsx'))
    >>> exch.read()
    >>> print(exch.data)

    * Write a new Excel File from scratch

    >>> exc = Excel(None)
    >>> out_file = os.path.join('maplearn path', 'tmp', 'scratch.xlsx')
    >>> df = pd.DataFrame({'A' : 1,
                           'B' : pd.Timestamp('20130102'),
                           'C' : pd.Series(2,index=list(range(4))),
                           'D' : np.array([3] * 4,dtype='int64')})
    exc.write(path=out_file, data=df)
"""
from __future__ import print_function

import logging
import pandas as pd

from maplearn.filehandler.filehandler import FileHandler


from maplearn import logger

try:
    pd.core.format.header_style = None  # <--- Workaround for header formatting
except AttributeError:
    logger.debug('Deprecated with this pandas version')


class Csv(FileHandler):
    """
    Handler to read and write attributes in a text file. It inherits from the 
    abstract class *FileHandler*.
    
    Attributes:
    
        * FileHandler's attributes
    
    Args:

        * path (str): path to the Csv file to open
    """

    def __init__(self, path):
        super(Csv, self).__init__(path=path, format='Csv')

    def open_(self):
        """
        Opens the CSV file specified in dsn['path']
        """
        FileHandler.open_(self)

    def read(self):
        """
        Reads the content of the CSV file
        """
        FileHandler.read(self)
        # lecture du feuillet
        self.data = pd.read_csv(self.dsn['path'], sep=None, engine='python')
        logger.info(self)
        return self.data

    def write(self, path=None, data=None, overwrite=True, **kwargs):
        """
        Write specified attributes in a text File
        
        Args:
            * path (str): path to the Excel to create and write
            * data (pandas DataFrame): dataset to write in the Excel file
            * overwrite (bool): should the output Excel file be overwritten ?
        """
        FileHandler.write(self, path=path, data=data, overwrite=overwrite)
        if data is None:
            data = self.data
        data.to_csv(path, sep='\t', index=False)
        logger.info('Csv file written : %s', path)
