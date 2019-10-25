
# Copyright (C) 2010-2017 - Andreas Maier
# CONRAD is developed as an Open Source project under the GNU General Public License (GPL-3.0)

import inspect
import os
import re
import sys
import time

import jpype
import numpy as np

import pyconrad

try:
    import pycuda.gpuarray as gpuarray
except ImportError:
    pass


class ImageUtil:

    ########################
    #  Convert Grid/numpy  #
    ########################

    @staticmethod
    def grid_from_numpy(grid):
        return np.ndarray.view(pyconrad.PyGrid.from_numpy(grid))

    @staticmethod
    def numpy_from_grid(ndarray):
        return np.ndarray.view(pyconrad.PyGrid.from_grid(ndarray))

    #################
    #  Save Images  #
    #################

    @staticmethod
    def save_grid_as_tiff(grid, path):
        jpype.JPackage(
            'edu').stanford.rsl.conrad.utils.ImageUtil.saveAs(grid, path)

    @staticmethod
    def save_numpy_as_tiff(array, path):
        grid = ImageUtil.grid_from_numpy(array)
        jpype.JPackage(
            'edu').stanford.rsl.conrad.utils.ImageUtil.saveAs(grid, path)

    #################
    #  Load Images  #
    #################

    @staticmethod
    def grid_from_tiff(path):
        ij = jpype.JPackage('ij').IJ.openImage(path)
        if not ij:
            raise RuntimeError('Error opening file \'%s\'' % path)
        grid = jpype.JPackage(
            'edu').stanford.rsl.conrad.utils.ImageUtil.wrapImagePlus(ij)
        return grid

    @staticmethod
    def array_from_tiff(path):
        ij = jpype.JPackage('ij').IJ.openImage(path)
        if not ij:
            raise RuntimeError('Error opening file \'%s\'' % path)
        grid = jpype.JPackage(
            'edu').stanford.rsl.conrad.utils.ImageUtil.wrapImagePlus(ij)
        return ImageUtil.numpy_from_grid(grid)


def to_conrad_grid(img):

    if isinstance(img, pyconrad.edu().stanford.rsl.conrad.data.numeric.NumericGrid):
        grid = img
    elif isinstance(img, pyconrad.PyGrid):
        grid = img.grid
    elif isinstance(img, np.ndarray):
        grid = pyconrad.PyGrid.from_numpy(img.astype(
            pyconrad.java_float_dtype)).grid
    elif 'pycuda' in sys.modules and isinstance(img, gpuarray.GPUArray):
        grid = pyconrad.PyGrid.from_numpy(img.get().astype(
            pyconrad.java_float_dtype)).grid
    elif isinstance(img, list):
        imgs = np.stack(img)
        grid = pyconrad.PyGrid.from_numpy(imgs.astype(
            pyconrad.java_float_dtype)).grid
    elif 'torch.Tensor' in str(type(img)):
        grid = pyconrad.PyGrid.from_numpy(img.cpu().numpy().astype(pyconrad.java_float_dtype)).grid
    else:
        raise TypeError('Unsupported Type: %s' % type(img))

    return grid


def show_everything(wait_key_press=False, wait_window_close=False):
    previous_frame = inspect.currentframe().f_back
    locals = previous_frame.f_locals

    if wait_key_press or wait_window_close:
        (filename, line_number, function_name, lines, index) = inspect.getframeinfo(previous_frame)
        print('{filename}:{line_number}: {line}'.format(filename=filename, line_number=line_number, line=lines[0]))

    imshow(locals,
           silent_fail=True,
           wait_key_press=wait_key_press,
           wait_window_close=wait_window_close)


def imshow(img,
           title="",
           wait_key_press=False,
           wait_window_close=False,
           origin=None,
           spacing=None,
           auto_assume_channels=True,
           lut=None,
           run=None,
           run_args="",
           silent_fail=False):
    """Shows an image in ImageJ

    Arguments:
        img {np.ndarray,} -- img can be a numpy array, a CONRAD grid, a pycuda.gpuarray.Gpuarray

    Keyword Arguments:
        title {str} -- Title of ImageJ window (default: {""})
        wait_key_press {bool} -- Stops program until key in console is pressed (default: {False})
        wait_window_close {bool} -- Stops program until display window in closed (default: {False})
        origin {[type]} -- Origin of array for metric coordinates in ImageJ (default: {None})
        spacing {[type]} -- Spacing of array for metric coordinates in ImageJ (default: {None})
        auto_assume_channels {bool} -- Try to guess when the last dimension could be channel data
                                         (much smaller size than other dimensions)
        lut {str} -- Apply a lut. Choose from "Fire", "Grays", "Ice", "Spectrum", "3-3-2 RGB", "Red", "Blue", "Cyan",
                     "Magenta", "Yellow", "Red/Green" (alias for run)
        run {str} -- Run a ImageJ command with `run_args`
        run_args {str} -- Commands for ImageJ command `run_args`
    """
    import ij
    if 'PYCONRAD_HEADLESS' in os.environ:
        return

    if not title:
        try:
            previous_frame = inspect.currentframe().f_back
            (filename, line_number, function_name, lines, index) = inspect.getframeinfo(previous_frame)
            match = re.search(r'\(.+\)', lines[0], re.DOTALL)
            title = match[0][1:-1]
        except Exception:
            pass

    class ImageListener:
        def __init__(self, image_plus=None):

            self.is_open = True
            self.image_plus = image_plus

        def imageOpened(self, imagePlus):
            pass

        def imageClosed(self, imagePlus):
            if imagePlus == self.image_plus or not self.image_plus:
                self.is_open = False

        def imageUpdated(self, imagePlus):
            pass

    if isinstance(img, dict):
        for i, (k, v) in enumerate(img.items()):
            imshow(v, str(k),
                   i == len(img.items()) - 1 and wait_key_press,
                   i == len(img.items()) - 1 and wait_window_close,
                   origin,
                   spacing,
                   auto_assume_channels,
                   lut,
                   run,
                   run_args,
                   silent_fail)

        return

    if not pyconrad.is_gui_started():
        pyconrad.start_gui()

    if isinstance(img, np.ndarray) and auto_assume_channels:
        if all(s > 10 for s in img.shape[:-1]) and img.shape[-1] < 10:
            img = np.moveaxis(img, -1, 0)

    if silent_fail:
        try:
            grid = to_conrad_grid(img)
        except Exception:
            return
    else:
        grid = to_conrad_grid(img)

    if origin:
        assert len(
            origin) == grid.ndim, 'spacing\'s length needs to match the number of dimensions of the grid'
        grid.setOrigin(origin)
    else:
        origin = list(grid.getOrigin())
    if spacing:
        assert len(
            spacing) == grid.ndim, 'origins\'s length needs to match the number of dimensions of the grid'
        grid.setSpacing(spacing)
    else:
        spacing = list(grid.getSpacing())
        if all(s == 0 for s in spacing):
            spacing = (1,) * max(grid.ndim, 3)

    listener = ImageListener()
    proxy = jpype.JProxy("ij.ImageListener", inst=listener)
    pyconrad.ij().ImagePlus.addImageListener(proxy)

    window = pyconrad.ij().WindowManager.getImage(title) if title else None

    if window:
        imageplus = pyconrad.stanfordrsl().conrad.utils.ImageUtil.wrapGrid(grid, title)
        window.setImage(imageplus)
    else:
        grid.show(title)
        window = pyconrad.ij().WindowManager.getImage(
            title) if title else ij.WindowManager.getCurrentWindow().getImagePlus()

    calibration = window.getCalibration()
    calibration.pixelWidth = spacing[-1]
    if len(spacing) >= 2:
        calibration.pixelHeight = spacing[-2]
    if len(spacing) >= 3:
        calibration.pixelDepth = spacing[-3]
    calibration.xOrigin = 0
    if len(origin) >= 2:
        calibration.yOrigin = 0
    if len(origin) >= 3:
        calibration.zOrigin = 0

    if run:
        ij.IJ.run(window, run, run_args)
        window.close()

    if lut:
        ij.IJ.run(window, lut, '')

    if listener and wait_window_close:
        while listener.is_open:
            time.sleep(0.1)
        pyconrad.ij().WindowManager.closeAllWindows()

    if wait_key_press:
        input("press key")
