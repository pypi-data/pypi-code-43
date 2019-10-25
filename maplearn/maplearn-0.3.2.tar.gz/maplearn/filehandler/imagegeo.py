# -*- coding: utf-8 -*-
"""
Geographic Images (raster)

This class handles raster data with geographic dimension (projection system,
bounding box expressed with coordinates).

A raster data relies on:
    * a matrix of pixels (data)
    * geographic data (where to put this matrix on earth)

Example:
    >>> img = ImageGeo(os.path.join('maplearn_path', 'datasets',
                                    'landsat_rennes.tif'))
    >>> img.read()
    >>> print(img.data)
"""
from osgeo import gdal, gdalnumeric, osr, gdal_array
import numpy as np
import pandas as pd

gdal.UseExceptions()

from maplearn.filehandler.filehandler import FileHandler

from maplearn import logger

# Table de conversion vers Gdal types
NP2GDAL = {
  "uint8": 1,
  "int8": 1,
  "uint16": 2,
  "int16": 3,
  "uint32": 4,
  "int32": 5,
  "float16": 6,
  "float32": 6,
  "float64": 7,
  "complex64": 10,
  "complex128": 11,
}


class ImageGeo(FileHandler):
    """
    Handler of geographical rasters
    
    Args:
        * path (str): path to the raster file to read
        * fmt (str): format of the raster file ('GTiff'... see GDAL 
                     documentation)
    
    Attributes:
        * Several attributes are inherited from `FileHandler` class
    """

    def __init__(self, path=None, fmt='GTiff'):
        super(ImageGeo, self).__init__(path=path, format=fmt)
        self.__geo = {'transf': None, 'prj': None}  # attributs geographiques (projection...)
        self.dims = None
        self.__ds = None

    def open_(self):
        """
        Opens the Geographical Image to get information about projection
        system...
        """
        FileHandler.open_(self)
        try:
            self.__ds = gdal.Open(self.dsn['path'])
        except RuntimeError:
            raise IOError("Can't read %s" % self.dsn['path'])
        self.__get_geo()

    def __get_geo(self):
        """
        Get geographical metadata (projection system...)
        """
        self.__geo['transf'] = self.__ds.GetGeoTransform()
        self.__geo['prj'] = self.__ds.GetProjectionRef()
        
    def read(self, dtype=None):
        """
        Reads the raster file and puts the matrix in `data` property
        
        Args:
            * dtype (str): type values stored in pixels (int, float...)
        """
        if self.__ds is None:
            self.open_()

        FileHandler.read(self)
        try:
            data = gdalnumeric.LoadFile(self.dsn['path'])
        except RuntimeError:
            raise IOError("Can't read %s" % self.dsn['path'])
        if data.ndim == 2:
            data = data[np.newaxis,:,:]
        
        self.__set_data(np.transpose(data, axes=(2,1,0)), dtype)
        logger.info("Raster data loaded from %s", self.dsn['path'])

    def set_geo(self, transf=None, prj=None):
        """
        Sets geographical dimension of a raster:
            * the projection system
            * the bounding box, whose coordinates are compatible with the given
            projection system
        
        Args:
            * prj (str): projection system
            * transf (list): affine function to translate an image

        Definition of 'transf' (to translate an image to the right place):
        [0] = top left x (x Origin)
        [1] = w-e pixel resolution (pixel Width)
        [2] = rotation, 0 if image is "north up"
        [3] = top left y (y Origin)
        [4] = rotation, 0 if image is "north up"
        [5] = n-s pixel resolution (pixel Height)
                
        TODO : 
            * Check compatibility between bounding box and image size
            * Adds EPSG code corresponding to `prj` in __geo
        """
        if not transf is None:
            self.__geo['transf'] = transf
        if not prj is None:
            self.__geo['prj'] = prj

    def init_data(self, dims, dtype=None):
        """
        Creates an empty matrix with specified dimension
        
        Args:
            * dims (list): dimensions of the image to create
            * dtype (str): numerical type of pixels
        """
        if not dtype is None:
            self.__set_data(np.zeros(dims, dtype), dtype)
        else:
            self.__set_data(np.zeros(dims))

    @property
    def data(self):
        """
        The dataset read from a file or to write in a file
        """
        return self._data

    @data.setter
    def data(self, data, dtype=None):
        self.__set_data(data, dtype)

    def __set_data(self, data, dtype=None):
        """
        Sets the data (overwrite if it already exists)
        
        Args:
            * data (array): data to use
            * dtype (str): type of numerical values
        """
        # gdal_array.NumericTypeCodeToGDALTypeCode(dtype)
        if dtype is None:
            self.dsn['depth'] = np.typeDict[str(data.dtype)]
        else:
            self.dsn['depth'] = dtype
            data = np.copy(data).astype(dtype)
        self._data = np.copy(data)
        self.dims = data.shape
        logger.info("Image with %i dimensions (%s)", data.ndim,
                    self.dsn['depth'])

    def xy2pixel(self, lon, lat):
        """
        Computes the position in an image (column, row), given a geographic 
        coordinate
        
        Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
        the pixel location of a geospatial coordinate
        (http://geospatialpython.com/2011/02/clip-raster-using-shapefile.html)
        
        Args:
            * lon (float): longitude (X)
            * lat (float): latitude (Y)
        
        Returns:
            list with the position in the image (column, row) 
        """
        lon, lat = float(lon), float(lat)
        ul_lon = self.__geo['transf'][0]
        ul_lat = self.__geo['transf'][3]
        lon_delta = self.__geo['transf'][1]
        lat_delta = abs(self.__geo['transf'][5])
        j = int(round((ul_lat - lat) / lat_delta))  # coordonnée en ligne
        i = int(round((lon - ul_lon) / lon_delta))  # coordonnée en colonne

        if i < 0 or i > self.dims[0] or j < 0 or j > self.dims[1]:
            logger.warning("(%f,%f) hors de l'image", lon, lat)
            return None
        return (i, j)

    def pixel2xy(self, j, i):
        """
        Computes the geographic coordinate (X,Y) corresponding to the specified
        position in an image (column, row)
        
        It does the inverse calculation of xy2pixel, and uses a gdal geomatrix             

        Source:
        http://geospatialpython.com/2011/02/clip-raster-using-shapefile.html
        
        Args:
            * j (int): column position
            * i (int): row position
        
        Returns:
            list: geographical coordinate of the pixel (lon and lat)            
        """
        if i < 0 or i > self.dims[1] or j < 0 or j > self.dims[0]:
            logger.warning("(%i,%i) hors de l'image (%i,%i)", i, j,
                            self.dims[0], self.dims[1])
            return None
        i, j = int(i), int(j)
        ul_lon = self.__geo['transf'][0]
        ul_lat = self.__geo['transf'][3]
        lon_delta = self.__geo['transf'][1]
        lon_dist = self.__geo['transf'][5]
        lon = (ul_lon + (j * lon_delta))
        lat = (ul_lat + (i * lon_dist))
        return (lon, lat)

    def write(self, path=None, data=None, overwrite=True, **kwargs):
        """
        Writes a data in a raster file
        
        Args:
            * path (str): raster file to write data into
            * data (array): data to write
            * overwrite (bool): should the raster file be overwritten?
        """
        if data is None:
            data = self._data
        
        # get metadata
        __meta = {'Title': 'Predicted by Mapping Learning'}
        if 'columns' in kwargs:
            for i, v in enumerate(kwargs['columns']):
                __meta['Band %i' % (i + 1)] = str(v)
        
        na = None
        if 'na' in kwargs:
            na = kwargs['na']
        if 'origin' in kwargs and not kwargs['origin'] is None:
            self.dsn['path'] = kwargs['origin']
            self.read()
            data = self.data_2_img(data, True, na=na)
        FileHandler.write(self, path, data, overwrite)
        # Creates the output raster file
        if self._drv is None:
            self._drv = gdal.GetDriverByName(self.dsn['format'])

        if 'epsg' in kwargs:
            self.__geo['epsg'] = kwargs['epsg']
        if 'epsg' in self.__geo:
            logger.debug('ESPG used to write : %s', self.__geo['epsg'])

        if 'depth' in kwargs:
            self.dsn['depth'] = kwargs['depth']
            logger.debug('Depth pixel used to write : %s', self.dsn['depth'])

        # convert into types that GDAL can use
        try:
            dtype = NP2GDAL[self.dsn['depth']]
        except KeyError:
            dtype = None
        if dtype is None:
            try:
                dtype = gdal_array.NumericTypeCodeToGDALTypeCode(self.dsn['depth'])
            except TypeError:
                dtype = gdal.GDT_Float64
                logger.error('dtype expected, got %s => "Float64" \
                             will be used instead', self.dsn['depth'], dtype)

        if data.ndim == 2 or data.shape[2] == 1:
            dst_ds = self._drv.Create(self.dsn['path'], self.dims[0],
                                      self.dims[1], 1, dtype)
        elif data.ndim == 3:
            dst_ds = self._drv.Create(self.dsn['path'], self.dims[0],
                                      self.dims[1], data.shape[2], dtype)
        else:
            raise ValueError("Unable to write a %i dimension(s) image"
                             % self._data.ndim)
        # write metadata into file
        try:
            dst_ds.SetMetadata(__meta)
        except TypeError:
            logger.warning('Metadata not well parsed. Can not be saved in %',
                           self.dsn['path'])
        # register data
        if not self.__geo['transf'] is None:
            dst_ds.SetGeoTransform(self.__geo['transf'])

        # project data
        if not self.__geo['prj'] is None:
            dst_ds.SetProjection(self.__geo['prj'])
            logger.debug('Projection system: %s', self.__geo['prj'])

        elif 'epsg' in self.__geo:
            sref = osr.SpatialReference()
            sref.ImportFromEPSG(self.__geo['epsg'])
            dst_ds.SetProjection(sref.ExportToPrettyWkt())
        else:
            logger.warning('No projection system given')
        # export
        if data.ndim == 2:
            dst_ds.GetRasterBand(1).WriteArray(np.transpose(data))
        elif data.ndim == 3:
            for i in range(1, data.shape[2] + 1):
                try:
                    band = dst_ds.GetRasterBand(i)
                except RuntimeError:
                    logger.warning('Issue to write band %i', i)
                else:
                    __md = band.GetMetadata()
                    try:
                        __name = __meta['Band %i' % i]
                    except KeyError:
                        __name = 'Band %i' %i
                    __md['NAME'] = __name
                    band.SetDescription(__name)
                    band.SetMetadata(__md)
                    band.WriteArray(np.transpose(data[:, :, i-1]))
                    band.ComputeStatistics(True)
                    logger.info('Statistics band %i computed', i)
        dst_ds = None
        logger.info('Image %s saved', self.dsn['path'])

    def data_2_img(self, data, overwrite=False, na=None):
        """
        Transforms a data set (dataframe) into a matrix in order to export it
        as an image (inverse operation to __img_2_data () method).
        
        Args:
            * data (dataframe): the dataset to transform
            * overwrite (bool): should the result `data` property ?
        
        Returns:
            matrix: transformed dataset
        """
        if isinstance(data, pd.DataFrame):
            logger.debug('Converting dataframe to matrix...')
            data = data.values

        if data.ndim == 1:
            data = np.expand_dims(data, axis=1)
        #TODO: handle NA
        if np.any(np.isnan(self._data)) or np.any(self._data==na):
            logger.debug('Handling NA')
            img = np.ones((self.dims[0], self.dims[1], data.shape[1]))
            img[np.any(np.isnan(self._data), axis=2)] = np.nan
            img[np.any(self._data==na, axis=2)] = np.nan
            img[np.all(~np.isnan(img), axis=2)] = data
            img[np.isnan(img)] = na # recoding NA using specified code
        else:
            logger.debug('No NA to handle in data')
            img = np.reshape(data,
                             (self.dims[0], self.dims[1], data.shape[1]))
        if overwrite:
            #self.init_data(img.shape)
            self.__set_data(img)
        return img

    def img_2_data(self):
        """
        Transforms the data set in order to make it easier to handle in
        following steps.
        
        Converts the data set (matrix) into to 2 dimensions dataframes (where 1
        line = 1 individual and 1 column = 1 feature)
        
        Returns:
            dataframe: transformed dataset (2 dimensions)
        """
        if self._data.ndim == 3:
            data = pd.DataFrame(np.reshape(self._data,
                            (self.dims[0] * self.dims[1], self.dims[2])))
        else:
            data = pd.DataFrame(self._data)
        #self._data = data
        return data

    def __del__(self):
        self.__ds = None