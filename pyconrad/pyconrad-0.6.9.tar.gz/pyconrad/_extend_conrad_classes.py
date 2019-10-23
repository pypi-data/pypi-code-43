
# Copyright (C) 2010-2017 - Andreas Maier
# CONRAD is developed as an Open Source project under the GNU General
# Public License (GPL-3.0)

from os.path import splitext

import numpy as np
from jpype import JArray, JClass, JDouble, JInt, JPackage, JProxy

import pyconrad
from pyconrad._java_pyconrad import JavaPyConrad

from ._imageutils import ImageUtil
from ._pygrid import PyGrid
from .constants import java_float_dtype

try:
    import pyconrad._vtk
except Exception:
    import warnings
    warnings.warn("Could not import pyconrad._vtk")

try:
    import jpype.beans  # noqa
except ImportError:
    pass


try:
    import pyopencl as cl
except Exception:
    cl = None


def _not_implemented_function(self):
    raise NotImplementedError('Not implemented yet')


def _extend_pointnd():
    @classmethod
    def _pointnd_from_numpy(cls, array):
        return cls(JArray(JDouble)(array.tolist()))

    @classmethod
    def _pointnd_from_list(cls, array):
        return cls(JArray(JDouble)(array))

    def _numpy_pointnd(self):
        return np.array(self.getCoordinates()[:])

    pointnd_class = JPackage(
        'edu').stanford.rsl.conrad.geometry.shapes.simple.PointND
    pointnd_class.as_numpy = _numpy_pointnd
    pointnd_class.from_numpy = _pointnd_from_numpy
    pointnd_class.from_list = _pointnd_from_list


def _extend_simple_vector():
    @classmethod
    def _simple_vector_from_numpy(cls, array):
        return cls(JArray(JDouble)(array.tolist()))

    @classmethod
    def _simple_vector_from_list(cls, array):
        return cls(JArray(JDouble)(array))

    def _numpy_simple_vector(self):
        return np.array(self.copyAsDoubleArray())

    simple_vector_class = JPackage(
        'edu').stanford.rsl.conrad.numerics.SimpleVector
    simple_vector_class.as_numpy = _numpy_simple_vector
    simple_vector_class.from_numpy = _simple_vector_from_numpy
    simple_vector_class.from_list = _simple_vector_from_list


def _extend_simple_matrix():
    @classmethod
    def _simple_matrix_from_numpy(cls, array):
        return cls(JArray(JDouble, np.ndim(array))(np.array(array).tolist()))

    @classmethod
    def _simple_matrix_from_list(cls, array):
        return cls(JArray(JDouble, np.ndim(array))(array))

    def _numpy_simple_matrix(self):
        return np.array(self.copyAsDoubleArray())

    @property
    def _simple_matrix_shape(self):
        return (self.rows, self.cols)

    @property
    def _simple_matrix_rows(self):
        return self.getRows()

    @property
    def _simple_matrix_cols(self):
        return self.getCols()

    simple_matrix_class = JPackage(
        'edu').stanford.rsl.conrad.numerics.SimpleMatrix
    simple_matrix_class.as_numpy = _numpy_simple_matrix
    simple_matrix_class.from_numpy = _simple_matrix_from_numpy
    simple_matrix_class.from_list = _simple_matrix_from_list
    simple_matrix_class.shape = _simple_matrix_shape
    simple_matrix_class.cols = _simple_matrix_cols
    simple_matrix_class.rows = _simple_matrix_rows


def _extend_imageplus():
    @classmethod
    def _imageplus_from_numpy(cls, array, title=""):
        # jpype.JPackage('edu').stanford.rsl.conrad.utils.ImageUtil.wrapImagePlus()
        grid = JPackage(
            'edu').stanford.rsl.conrad.data.numeric.NumericGrid.from_numpy(array)
        return JPackage('edu').stanford.rsl.conrad.utils.ImageUtil.wrapGrid(grid, title)

    def _imageplus_as_numpy(self):
        # jpype.JPackage('edu').stanford.rsl.conrad.utils.ImageUtil.wrapImagePlus()
        grid = JPackage(
            'edu').stanford.rsl.conrad.utils.ImageUtil.wrapImagePlus(self)

        return grid.as_numpy()

    def _imageplus_as_grid(self):
        # jpype.JPackage('edu').stanford.rsl.conrad.utils.ImageUtil.wrapImagePlus()
        grid = JPackage(
            'edu').stanford.rsl.conrad.utils.ImageUtil.wrapImagePlus(self)
        return grid

    imageplus_class = JPackage('ij').ImagePlus

    imageplus_class.from_numpy = _imageplus_from_numpy
    imageplus_class.as_numpy = _imageplus_as_numpy
    imageplus_class.__array__ = _imageplus_as_numpy
    imageplus_class.as_grid = _imageplus_as_grid


def _extend_numeric_grid():

    @classmethod
    def _numeric_grid_from_numpy(cls, array):
        return PyGrid.from_numpy(np.array(array, java_float_dtype)).grid

    @classmethod
    def _numeric_grid_from_list(cls, input_list):
        return PyGrid.from_numpy(np.array(input_list, java_float_dtype)).grid

    @classmethod
    def _numeric_grid_from_size(cls, *size):
        return PyGrid(list(size)).grid

    @classmethod
    def _numeric_grid_from_shape(cls, *shape):
        return PyGrid(list(reversed(shape))).grid

    def _numpy_grid(self, dtype=pyconrad.java_float_dtype):
        return np.array(PyGrid.from_grid(self), dtype)

    def _numpy_grid_as_imageplus(self, title=""):
        return JPackage('edu').stanford.rsl.conrad.utils.ImageUtil.wrapGrid(self, title)

    def _numeric_grid_getitem(self, idxs):
        if isinstance(idxs, int) and not isinstance(self, JPackage('edu').stanford.rsl.conrad.data.numeric.Grid1D):
            return self.getSubGrid(idxs)
        elif isinstance(idxs, slice) and \
            (isinstance(self, JPackage('edu').stanford.rsl.conrad.data.numeric.Grid3D) or
             (isinstance(self, JPackage('edu').stanford.rsl.conrad.data.numeric.Grid4D))):
            start = idxs.start or 0
            end = idxs.stop or self.getSize()[2]
            assert idxs.step == 1 or not idxs.step, "Only step==1 is supported"

            rtn = self.type(
                reversed(*self.getSize()[:]), self.getsize()[1], end - start, False)
            # rtn =
            # pyconrad.PyConrad().classes.stanford.rsl.conrad.data.numeric.Grid3D(self.getSize()[0],self.getSize()[1],
            # end - start, False)
            rtn.setOrigin(self.getOrigin())
            rtn.setSpacing(self.getSpacing())
            for i in range(start, end):
                rtn.setSubGrid(i - start, self.getSubGrid(i))
            return rtn
        else:
            return self.getValue(idxs)

    def _numeric_grid_setitem(self, idxs, value):
        if isinstance(idxs, int) and not isinstance(self, JPackage('edu').stanford.rsl.conrad.data.numeric.Grid1D):
            return self.setSubGrid(idxs, value)
        elif isinstance(idxs, tuple):
            return self.setValue(value, JArray(JInt)(idxs))
        else:
            raise ValueError('not implemented')

    @property
    def _numeric_grid_shape(self):
        return tuple(reversed(self.getSize()[:]))

    @property
    def _numeric_grid_size(self):
        return tuple(self.getSize()[:])

    @property
    def _numeric_grid_ndim(self):
        return len(self.getSize()[:])

    @property
    def _pygrid(self):
        return PyGrid.from_grid(self)

    @property
    def _numeric_origin(self):
        return self.getOrigin()

    @property
    def _numeric_spacing(self):
        return self.getOrigin()

    def _save_as_tiff(self, path):
        ImageUtil.save_grid_as_tiff(self, path)

    def _save_as_vtk(self, path, title='vol'):
        _, ext = splitext(path)
        if ext.lower() == '.vti':
            path = path[:-4]

        from pyevtk.hl import imageToVTK
        if np.abs(self.getSpacing()[0]) < 1e-5:
            spacing = [1.] * len(self.shape)
        else:
            spacing = tuple(self.getSpacing()[:])
        imageToVTK(path, tuple(self.getOrigin()[
                   :]), spacing, pointData={title: np.swapaxes(np.array(self), 0, 2)})

    @staticmethod
    def _from_tiff(path):
        return ImageUtil.grid_from_tiff(path)

    @staticmethod
    def _from_vtk(path, array_idx=0):
        array, origin, spacing = pyconrad._vtk.read_vtk(path, array_idx)
        grid = JPackage(
            'edu').stanford.rsl.conrad.data.numeric.NumericGrid.from_numpy(array)
        grid.setOrigin(origin)
        grid.setSpacing(spacing)
        return grid

    grid_class = JPackage('edu').stanford.rsl.conrad.data.numeric.NumericGrid
    grid_class.as_numpy = _numpy_grid
    grid_class.as_imageplus = _numpy_grid_as_imageplus
    grid_class.from_numpy = _numeric_grid_from_numpy
    grid_class.from_list = _numeric_grid_from_list
    grid_class.from_size = _numeric_grid_from_size
    grid_class.from_shape = _numeric_grid_from_shape
    grid_class.from_tiff = _from_tiff
    grid_class.from_vtk = _from_vtk
    grid_class.from_image = _from_tiff
    grid_class.save_tiff = _save_as_tiff
    grid_class.save_vtk = _save_as_vtk
    grid_class.__getitem__ = _numeric_grid_getitem
    grid_class.__setitem__ = _numeric_grid_setitem
    grid_class.shape = _numeric_grid_shape
    grid_class.size = _numeric_grid_size
    grid_class.spacing = _numeric_spacing
    grid_class.origin = _numeric_origin
    grid_class.ndim = _numeric_grid_ndim
    grid_class.pygrid = _pygrid
    grid_class.__array__ = _numpy_grid


def _extend_ocl_grids():
    @staticmethod
    def _oclgrid_from_numpy(numpy):
        grid = getattr(JPackage('edu').stanford.rsl.conrad.data.numeric,
                       'Grid%iD' % numpy.ndim)(*reversed(numpy.shape))
        oclgrid = getattr(
            JPackage('edu').stanford.rsl.conrad.data.numeric.opencl,
            'OpenCLGrid%iD' % numpy.ndim)(grid)
        oclgrid.getDelegate().hostChanged = False
        oclgrid.getDelegate().deviceChanged = True

        numpy = numpy.astype(np.float32)

        queue = pyconrad.opencl.get_conrad_command_queue()
        cl_buffer = cl.Buffer.from_int_ptr(
            oclgrid.getDelegate().getCLBuffer().ID)
        cl.enqueue_copy(queue, cl_buffer, numpy)
        return oclgrid

    def _oclgrid_upload_numpy(self, numpy):

        numpy = numpy.astype(np.float32)

        queue = pyconrad.opencl.get_conrad_command_queue()
        cl_buffer = cl.Buffer.from_int_ptr(
            self.getDelegate().getCLBuffer().ID)
        self.getDelegate().hostChanged = False
        self.getDelegate().deviceChanged = True
        cl.enqueue_copy(queue, cl_buffer, numpy)

    def _oclgrid_download_numpy(self, numpy=None):

        if numpy is None:
            numpy = np.ndarray(self.shape, np.float32)
        else:
            if not numpy.dtype == np.float32:
                raise TypeError('ndarray must be of dtype float32')
            if not numpy.shape == self.shape:
                raise TypeError(
                    'ndarray must have the same shape as the OCL grid')

        queue = pyconrad.opencl.get_conrad_command_queue()
        cl_buffer = cl.Buffer.from_int_ptr(
            self.getDelegate().getCLBuffer().ID)
        cl.enqueue_copy(queue, numpy, cl_buffer)

        return numpy

    @staticmethod
    def _oclgrid_from_tiff(path):
        grid = ImageUtil.grid_from_tiff(path)
        clgrid_class = JClass(
            'edu.stanford.rsl.conrad.data.numeric.opencl.OpenCLGrid%iD' % grid.ndim)
        clgrid = clgrid_class(grid)
        return clgrid

    # @staticmethod
    # def _oclgrid_from_clarray(clarray):

    #     return clgrid

    @staticmethod
    def _oclgrid_from_size(size):
        grid = PyGrid(list(reversed(size))).grid
        return getattr(pyconrad.opencl.opencl_namespaces, 'OpenCLGrid%iD' % grid.ndim)(grid)

    @staticmethod
    def _oclgrid_from_shape(shape):
        grid = PyGrid(list(shape)).grid
        return getattr(pyconrad.opencl.opencl_namespaces, 'OpenCLGrid%iD' % grid.ndim)(grid)

    def _oclgrid_as_clbuffer(self):
        self.getDelegate().prepareForDeviceOperation()
        clbuffer = cl.Buffer.from_int_ptr(
            self.getDelegate().getCLBuffer().ID)
        return clbuffer

    @staticmethod
    def _oclgrid_from_clarray(clarray):

        # TODO: still needs copy!

        grid_class = getattr(JPackage('edu').stanford.rsl.conrad.data.numeric,
                             'Grid%iD' % clarray.ndim)
        int_size = reversed([int(i) for i in clarray.shape])
        grid = grid_class(*int_size)
        oclgrid = getattr(
            JPackage('edu').stanford.rsl.conrad.data.numeric.opencl,
            'OpenCLGrid%iD' % clarray.ndim)(grid)
        oclgrid.getDelegate().hostChanged = False
        oclgrid.getDelegate().deviceChanged = True

        assert clarray.dtype == np.float32

        queue = pyconrad.opencl.get_conrad_command_queue()
        cl_buffer = cl.Buffer.from_int_ptr(
            oclgrid.getDelegate().getCLBuffer().ID)
        cl.enqueue_copy(queue, cl_buffer, clarray.data)
        return oclgrid

    def _oclgrid_as_clarray(self):
        self.getDelegate().prepareForDeviceOperation()
        clbuffer = cl.Buffer.from_int_ptr(
            self.getDelegate().getCLBuffer().ID)
        return cl.array.Array(pyconrad.opencl.get_conrad_command_queue(), tuple(self.shape), np.float32, data=clbuffer)

    for i in range(1, 4):
        clgrid_class = JClass(
            'edu.stanford.rsl.conrad.data.numeric.opencl.OpenCLGrid%iD' % i)
        clgrid_class.from_numpy = _oclgrid_from_numpy
        clgrid_class.from_tiff = _oclgrid_from_tiff
        clgrid_class.from_image = _oclgrid_from_tiff
        clgrid_class.download_numpy = _oclgrid_download_numpy
        clgrid_class.upload_numpy = _oclgrid_upload_numpy
        clgrid_class.from_list = _not_implemented_function
        clgrid_class.from_size = _oclgrid_from_size
        clgrid_class.from_shape = _oclgrid_from_shape
        clgrid_class.as_clbuffer = _oclgrid_as_clbuffer
        clgrid_class.as_clarray = _oclgrid_as_clarray
        clgrid_class.from_clbuffer = _not_implemented_function
        clgrid_class.from_clarray = _oclgrid_from_clarray


def _extend_pyconrad_java():
    pyconrad_class = JClass(
        'edu.stanford.rsl.conrad.pyconrad.PyConrad')
    callback = JProxy(
        "edu.stanford.rsl.conrad.pyconrad.PythonCallback", inst=JavaPyConrad())
    pyconrad_class.pythonCallback = callback


def extend_all_classes():
    __setattr = JClass.__setattr__
    JClass.__setattr__ = type.__setattr__
    _extend_pointnd()
    _extend_simple_vector()
    _extend_simple_matrix()
    _extend_numeric_grid()
    _extend_imageplus()
    _extend_pyconrad_java()
    if cl:
        _extend_ocl_grids()
    JClass.__setattr__ = __setattr
