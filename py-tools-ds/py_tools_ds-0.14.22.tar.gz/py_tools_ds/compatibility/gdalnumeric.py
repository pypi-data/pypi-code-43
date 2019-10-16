# -*- coding: utf-8 -*-

# py_tools_ds
#
# Copyright (C) 2019  Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
#
# This software was developed within the context of the GeoMultiSens project funded
# by the German Federal Ministry of Education and Research
# (project grant code: 01 IS 14 010 A-C).
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Daniel Scheffler"

try:
    from osgeo import gdal
    from osgeo import gdalnumeric
except ImportError:
    import gdal
    import gdalnumeric  # FIXME this will import this __module__


def OpenNumPyArray(array):
    """This function emulates the functionality of gdalnumeric.OpenNumPyArray() which is not available in GDAL versions
     below 2.1.0 (?).

    :param array:   <numpy.ndarray> in the shape (bands, rows, columns)
    :return:
    """
    if array.ndim == 2:
        rows, cols = array.shape
        bands = 1
    elif array.ndim == 3:
        bands, rows, cols = array.shape
    else:
        raise ValueError('OpenNumPyArray() currently only supports 2D and 3D arrays. Given array shape is %s.'
                         % str(array.shape))

    # get output datatype
    gdal_dtype = gdalnumeric.NumericTypeCodeToGDALTypeCode(array.dtype)  # FIXME not all datatypes can be translated
    assert gdal_dtype is not None, 'Datatype %s is currently not supported by OpenNumPyArray().' % array.dtype

    mem_drv = gdal.GetDriverByName('MEM')
    mem_ds = mem_drv.Create('/vsimem/tmp/memfile.mem', cols, rows, bands, gdal_dtype)

    if mem_ds is None:
        raise Exception(gdal.GetLastErrorMsg())

    for bandNr in range(bands):
        band = mem_ds.GetRasterBand(bandNr + 1)
        band.WriteArray(array[:, :, bandNr] if bands > 1 else array)
        del band

    mem_ds.FlushCache()  # Write to disk.
    return mem_ds


def get_gdalnumeric_func(funcName):
    try:
        return getattr(gdalnumeric, funcName)
    except AttributeError:
        if funcName in globals():
            return globals()[funcName]
        else:
            raise AttributeError("'gdalnumeric' has no attribute '%s'." % funcName)
