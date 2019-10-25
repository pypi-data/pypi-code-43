"""
Handling files (abstract class)


This class is to handle generic files. FileHandler is not supposed to be called
directly. Use rather one of the classes that inherits from it (ImageGeo, Excel,
Shapefile...).

"""
import logging
import os

from maplearn import logger


class FileHandler(object):
    """
    Reads data from a generic file or write data into it.
    
    Attributes:
        * _drv (object): driver to communicate with a file (necessary for some
                         formats)
        * _data (numpy array or pandas dataframe): dataset got from a file or
                to write into it. See `data` property.
        * opened (bool): is the file opened or not ?

    Args:
        * path (str): path the file to read data from
        * **kwargs: additional settings to specify how to load data from file
    """

    def __init__(self, path=None, **kwargs):
        self.__dsn = {'path': None}
        self._drv = None
        self._data = None
        self.opened = False
        kwargs['path'] = path
        self.__set_dsn(**kwargs)

    @property
    def dsn(self):
        """
        Dictionnary containing informations about data source. For example,
        `path` contains the path of the file to get data from. Other items can
        exist, which are specific to the data type (raster, vector or tabular,
        geographical or not...)
        """
        return self.__dsn

    @dsn.setter
    def dsn(self, **kwargs):
        self.__set_dsn(kwargs)

    def __set_dsn(self, **kwargs):
        """
        Sets the content of __dsn private attribute, which is usable outside 
        the class thanks to the `dsn` property.
        """
        # reinitialisation source de donnees
        if 'path' in kwargs and not kwargs['path'] is None:
            logger.info('File : %s', self.__dsn['path'])

        for key, value in kwargs.items():
            self.__dsn[key] = value
        if self.__dsn['path'] is None:
            logger.warning("No file to get data from specified")

    @property
    def data(self):
        """
        The dataset read from a file or to write in a file
        """
        return self._data

    @data.setter
    def data(self, data):
        """
        Sets the dataset
        
        Args:
            data (numpy array or pandas dataframe): dataset to write in a file
        """
        self._data = data

    def open_(self):
        """
        Opens a file prior to write in it
        """
        if self.__dsn['path'] is None or not os.path.exists(self.__dsn['path']):
            logger.info('File %s is missing', self.__dsn['path'])
            self.opened = False
        else:
            logger.info('File %s found', self.__dsn['path'])            
            self.opened = True

    def read(self):
        """
        Reads the dataset from the file mentioned during initialization
        """
        self._data = None
        if not self.opened:
            self.open_()
        if not self.opened:
            raise IOError('File to read %s is missing', self.__dsn['path'])
        logger.debug('Reading file %s...', self.__dsn['path'])

    def write(self, path=None, data=None, overwrite=True, **kwargs):
        """
        Writes data in a file
        
        Args:
            * path (str): path to the file to write into
            * data (numpy array or pandas dataframe): the data to write
            * overwrite (bool): should the file be overwritten if it exists ?
        """
        if not path is None:
            self.__set_dsn(path=path)
        if not data is None:
            self.data = data

        if self.data is None:
            raise ValueError('No data to write')

        if os.path.exists(self.__dsn['path']):
            if overwrite:
                logger.warning('File %s exists and will be overwritten',
                                self.__dsn['path'])
            else:
                str_msg = 'File %s already exists => end' % self.__dsn['path']
                logger.critical(str_msg)
                raise IOError(str_msg)

    def __str__(self):
        str_msg = ""
        lst_param = ['path', 'format']
        lst_param += [k for k in self.__dsn.keys() if k not in lst_param]
        for p in lst_param:
            str_msg += "%s : " % p.capitalize()
            if p in self.__dsn and not self.__dsn[p] is None:
                str_msg += "%s\n" % self.__dsn[p]
            else:
                str_msg += "Inconnu\n"

        if not self._data is None:
            str_msg += 'Donnees en stock : %i lignes - %i colonnes' % \
                       (self._data.shape[0], self._data.shape[1])
        return str_msg

    def __del__(self):
        self._drv = None
