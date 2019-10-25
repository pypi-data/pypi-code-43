# -*- coding: utf-8 -*-
"""
Excel file reader and writer

With this class, you can read an Excel file or write a new one with your own
dataset (Pandas Dataframe).

Examples:

    * Read an existing Excel file

    >>> exch = Excel(os.path.join('maplearn path', 'datasets', 'ex1.xlsx'))
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


class Excel(FileHandler):
    """
    Handler to read and write attributes in an Excel file. It inherits from the
    abstract class *FileHandler*.

    Attributes:

        * FileHandler's attributes

    Args:

        * path (str): path to the Excel file to open
        * sheet (str): name of the sheet to open
    """

    def __init__(self, path, sheet=None):
        super(Excel, self).__init__(path=path, sheet=sheet, format='Excel')

    def open_(self):
        """
        Opens the Excel file specified in dsn['path']
        """
        FileHandler.open_(self)

        self._drv = pd.ExcelFile(self.dsn['path'])

        # Default behavior : if the given sheet is not found, the 1st sheet is
        #                    used instead
        if self.dsn['sheet'] is None:
            logger.debug('No sheet given => the 1st will be used')
            self.dsn['sheet'] = self._drv.sheet_names[0]
        if self.dsn['sheet'] not in self._drv.sheet_names:
            logger.debug('Sheet %s is missing => Using the 1st one',
                         self.dsn['sheet'])
            self.dsn['sheet'] = self._drv.sheet_names[0]

    def read(self):
        """
        Reads the content of the opened Excel file
        """
        FileHandler.read(self)
        # lecture du feuillet
        self.data = self._drv.parse(self.dsn['sheet'])
        logger.info(self)
        return self.data

    def write(self, path=None, data=None, overwrite=True, **kwargs):
        """
        Write specified attributes in an Excel File

        Args:
            * path (str): path to the Excel to create and write
            * data (pandas DataFrame): dataset to write in the Excel file
            * overwrite (bool): should the output Excel file be overwritten ?
        """
        FileHandler.write(self, path=path, data=data, overwrite=overwrite)
        if data is None:
            data = self.data
        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter(path)
        data.to_excel(writer)
        writer.save()
        logger.info('Excel file written : %s', path)
