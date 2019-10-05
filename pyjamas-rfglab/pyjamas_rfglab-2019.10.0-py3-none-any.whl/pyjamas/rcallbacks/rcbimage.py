"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# todo:
# move gaussian filtering INSIDE the rimutils functions (find_seeds or waterseed)?

import time
from typing import List

import numpy
from PyQt5 import QtCore, QtWidgets
from shapely.geometry import Point
from scipy import ndimage
from scipy.spatial import ConvexHull
import skimage.filters

import pyjamas.dialogs as dialogs
from pyjamas.pjscore import PyJAMAS
from pyjamas.pjsthreads import Thread
from pyjamas.pjsthreads import ThreadSignals
from pyjamas.rcallbacks.rcallback import RCallback
from pyjamas.rimage.rimutils import rimutils
from pyjamas.rutils import RUtils


class RCBImage(RCallback):
    CW: int = 90
    CCW: int = -90
    UP_DOWN: int = 1
    LEFT_RIGHT: int = 2

    DEFAULT_WINDOW_SZ: int = 64
    DEFAULT_SMOOTHING_SIGMA: float = 0.8
    DEFAULT_BINARY_DILATIONS: int = -4  # positive to segment dark objects with brigh background, negative for the opposite.
    DEFAULT_MINIMUM_DISTANCE_TRANSFORM: float = 5.0
    DEFAULT_MAX_SEED_NUMBER: int = 100
    DEFAULT_PREVIEW: bool = False
    DEFAULT_ALPHA_CONCAVE_HULL: int = 25  # Trial and error ...
    _MIN_CELL_AREA: int = 10
    _MAX_CELL_AREA: int = 10000
    CENTER_SEEDS_CLOSER_TO_THE_EDGE: float = 6.0

    def cbAdjustContrast(self, min_percentile=None, max_percentile=None) -> bool:
        continue_flag = True

        if min_percentile is None or min_percentile is False or max_percentile is None or max_percentile is False:
            dialog = QtWidgets.QDialog()
            ui = dialogs.adjustcontrast.AdjustContrastDialog(self.pjs)
            ui.setupUi(dialog, self.pjs.min_pix_percentile, self.pjs.max_pix_percentile)
            dialog.exec_()
            dialog.show()

            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted

            if continue_flag:
                parameters = ui.parameters()
                min_percentile = parameters.get('min_percentile', 0)
                max_percentile = parameters.get('max_percentile', 100)

            dialog.close()

        if continue_flag:

            self.pjs.min_pix_percentile = min_percentile
            self.pjs.max_pix_percentile = max_percentile

            self.pjs.displayData()

            return True

        else:
            return False

    def cbRotateImage(self, direction: int = CW) -> bool:
        if direction == self.CW:
            # self.pjs.slices = numpy.asarray([numpy.rot90(x, -1) for x in self.pjs.slices]) # An order of magnitude slower than below.
            self.pjs.slices = numpy.rot90(self.pjs.slices, -1, (1, 2))

        elif direction == self.CCW:
            # self.pjs.slices = numpy.asarray([numpy.rot90(x) for x in self.pjs.slices]) # An order of magnitude slower than below.
            self.pjs.slices = numpy.rot90(self.pjs.slices, 1, (1, 2))

        self.pjs.initImage()

        return True

    def cbFlipImage(self, direction: int = LEFT_RIGHT) -> bool:
        if direction == self.LEFT_RIGHT:
            # self.pjs.slices = numpy.flip(self.pjs.slices, 2)  # Order or magnitude slower than the code below.
            self.pjs.slices = self.pjs.slices[..., ::-1]
        elif direction == self.UP_DOWN:
            # self.pjs.slices = numpy.fliplr(self.pjs.slices)  # Could have used flip with parameter 1, but this is faster. Unfortunately, there is no fast function to flip with parameter 2. Still, slower than below.
            self.pjs.slices = self.pjs.slices[..., ::-1, :]

        self.pjs.initImage()

        return True

    def cbMIPImage(self, slice_list: List[int]) -> bool:
        if slice_list is False:
            slice_list_str, ok_pressed = QtWidgets.QInputDialog.getText(None, "Maximum intenstiy projection", "Enter a range of slices (e.g. 0, 1, 4-8, 15): ", QtWidgets.QLineEdit.Normal, "")

            if not ok_pressed:
                return False

            if slice_list_str == '':
                slice_list = list(range(self.pjs.n_frames))
            else:
                slice_list = RUtils.parse_range_list(slice_list_str)

        # This line here is necessary: for some mysterious reason, if doing an MIP from a slice
        # other than the first one, there is an error that I was unable to debug, but seemed related
        # to the Qt backend based on the debugger error.
        """/Users/rodrigo/src/pyjamas/pyjamas/rimage/rimutils.py:641: RuntimeWarning: divide by zero encountered in true_divide
            sc = (maximum - minimum) / (high - low)
            /Users/rodrigo/src/pyjamas/pyjamas/rimage/rimutils.py:648: RuntimeWarning: invalid value encountered in multiply
            image_out = image_out * sc"""
        self.pjs.image.cbGoTo(0)

        self.pjs.slices = rimutils.mip(self.pjs.slices[slice_list])

        self.pjs.initImage()

        return True

    def cbInvertImage(self) -> bool:
        self.pjs.slices = rimutils.invert(self.pjs.slices)
        self.pjs.prepare_image()

        self.pjs.displayData()

        return True

    def cbRegisterImage(self) -> bool:
        working_slice = self.pjs.curslice
        self.pjs.slices, distances = rimutils.register(self.pjs.slices, RUtils.pjsfiducials_to_array(self.pjs.fiducials), self.pjs.curslice)
        self.shift_annotations(distances)
        self.pjs.prepare_image()
        self.pjs.image.cbGoTo(working_slice)

        self.pjs.displayData()

        return True

    # Inspiration for multithreading from: # Shamelessly stolen from https://www.mfitzp.com/article/multithreading-pyqt-applications-with-qthreadpool/
    def cbPlay(self) -> bool: # oh_no
        # If a thread is already running, jump to the end of the movie.
        if self.pjs.threadpool.activeThreadCount() > 0:
            self.pjs.image.cbGoTo(self.pjs.n_frames-1)

        athread = Thread(self.play_movie)
        athread.kwargs['progress_callback'] = athread.signals.progress
        #athread.signals.result.connect(self.print_output)
        athread.signals.finished.connect(self.thread_complete)
        athread.signals.progress.connect(self.progress_fn)

        self.pjs.threadpool.start(athread)

        return True

    def play_movie(self, progress_callback) -> bool: #execute_this_fn
        start = time.time()
        period = 1.0 / self.pjs.fps

        while self.pjs.curslice < self.pjs.n_frames - 1:
            if (time.time() - start) > period:
                start += period
                # Because this is the function that will run in a thread, it cannot
                # manipulate the gui (or errors will happen - gui manipulations must
                # be in the thread that owns the gui). Instead, we can emit a signal
                # when it corresponds, and the signal can be slotted in a function
                # in the main thread that modifies the gui.
                progress_callback.emit(self.pjs.curslice)

        return True

    def progress_fn(self, n):
        self.pjs.image.cbNextFrame()

    def thread_complete(self):
        self.pjs.image.cbGoTo(0)

    def shift_annotations(self, translation_vector: numpy.ndarray) -> bool:
        if translation_vector is False or translation_vector is None:
            return False

        for slice_index in range(self.pjs.n_frames):
            theshift = translation_vector[slice_index].astype(int)

            for fiducial_index, _ in enumerate(self.pjs.fiducials[slice_index]):
                 self.pjs.fiducials[slice_index][fiducial_index] += theshift

            for a_polyline in self.pjs.polylines[slice_index]:
                a_polyline.translate(QtCore.QPointF(theshift[0], theshift[1]))

        return True

    def cbCrop(self, coordinates: numpy.ndarray = None, new_window: bool = False) -> bool:
        """

        :param coordinates: ndarray with two columns containing the x, y coordinates of the region to crop.
        :param new_window: True if the cropped image should open in a new PyJAMAS session, False if the current window
        should be used instead.
        :return: False if no coordinates are provided, True otherwise.
        """
        if (not coordinates) | (coordinates is None) | (coordinates == []):
            thepolylines = self.pjs.polylines[self.pjs.curslice]

            if thepolylines != [] and thepolylines[0] != []:
                thepolyline = thepolylines[0].boundingRect()
                minx, miny, maxx, maxy = thepolyline.getCoords()

            else:
                return False

        else:
            # This is here mainly to crop around non-rectangular polylines.
            minx, miny = numpy.min(coordinates, axis=0)
            maxx, maxy = numpy.max(coordinates, axis=0)

        # Make sure you are working with integers to prevent errors when slicing the original image.
        minx, miny, maxx, maxy = numpy.int(minx), numpy.int(miny), numpy.int(maxx), numpy.int(maxy)
        cropped_image = self.pjs.slices[:, miny:(maxy+1), minx:(maxx+1)]

        # Open in current window or new window?
        if not new_window:
            # Crop.
            self.pjs.io.cbLoadArray(cropped_image)

        else:
            self.launch_thread(PyJAMAS.new_pjs, {'theimage': cropped_image})

            # Create new pyjamas and crop.
            #new_pjs: pjscore.PyJAMAS = pjscore.PyJAMAS()
            #new_pjs.io.cbLoadArray(cropped_image)

        return True

    def cbKymograph(self, coordinates: numpy.ndarray = None, new_window: bool = True) -> bool:
        """

        :param coordinates: ndarray with two columns containing the x, y coordinates of the region to crop.
        :param new_window: True if the cropped image should open in a new PyJAMAS session, False if the current window
        should be used instead.
        :return: False if no coordinates are provided, True otherwise.
        """
        if (not coordinates) | (coordinates is None) | (coordinates == []):
            thepolylines = self.pjs.polylines[self.pjs.curslice]

            if thepolylines != [] and thepolylines[0] != []:
                thepolyline = thepolylines[0].boundingRect()
                minx, miny, maxx, maxy = thepolyline.getCoords()

            else:
                return False

        else:
            # This is here mainly to crop around non-rectangular polylines.
            minx, miny = numpy.min(coordinates, axis=0)
            maxx, maxy = numpy.max(coordinates, axis=0)

        # Make sure you are working with integers to prevent errors when slicing the original image.
        coordinates: numpy.ndarray = numpy.asarray([[minx, miny], [maxx, maxy]])

        # Make kymograph.
        thekymo = rimutils.kymograph(self.pjs.slices, coordinates)

        # Open in current window or new window?
        if not new_window:
            self.pjs.io.cbLoadArray(thekymo)
        else:
            # Create a new window containing the cropped image.
            new_pjs: PyJAMAS = PyJAMAS()
            new_pjs.io.cbLoadArray(thekymo)

        return True

    def cbZoom(self):
        self.pjs.gView.scale(1./PyJAMAS.zoom_factors[self.pjs.zoom_index],
                             1./PyJAMAS.zoom_factors[self.pjs.zoom_index])
        self.pjs.zoom_index = (self.pjs.zoom_index+1) % len(PyJAMAS.zoom_factors)

        self.pjs.gView.scale(PyJAMAS.zoom_factors[self.pjs.zoom_index], PyJAMAS.zoom_factors[self.pjs.zoom_index])
        self.pjs.MainWindow.resize(self.pjs.width * self.pjs.zoom_factors[self.pjs.zoom_index],
                                   self.pjs.height * self.pjs.zoom_factors[self.pjs.zoom_index] + 60)
        self.pjs.statusbar.showMessage(str(self.pjs.curslice + 1) + '/' + str(self.pjs.n_frames) +
                                       ' zoom: ' + str(PyJAMAS.zoom_factors[self.pjs.zoom_index]) + 'x')

        return True

    def cbNextFrame(self):
        if self.pjs.curslice < self.pjs.n_frames - 1:
            self.pjs.curslice = self.pjs.curslice + 1
        elif self.pjs.curslice == self.pjs.n_frames - 1:
            self.pjs.curslice = 0

        self.pjs.imagedata = self.pjs.slices[self.pjs.curslice]
        self.pjs.timeSlider.setValue(self.pjs.curslice+1)

        self.pjs.displayData()

        return True

    def cbPrevFrame(self):
        if self.pjs.curslice > 0:
            self.pjs.curslice = self.pjs.curslice - 1
        elif self.pjs.curslice == 0:
            self.pjs.curslice = self.pjs.n_frames - 1

        self.pjs.imagedata = self.pjs.slices[self.pjs.curslice]
        self.pjs.timeSlider.setValue(self.pjs.curslice + 1)

        self.pjs.displayData()

        return True

    def cbTimeSlider(self) -> bool:
        self.pjs.curslice = self.pjs.timeSlider.value()-1
        self.pjs.imagedata = self.pjs.slices[self.pjs.curslice]

        self.pjs.displayData()

        return True

    def cbGoTo(self, slice_index: int) -> bool:
        """

        :param slice_index: negative values start start pointing from the last slice (-1 being the last one).
        :return:
        """
        if slice_index >= self.pjs.n_frames:
            return False

        if slice_index < 0:
            slice_index = self.pjs.n_frames+slice_index
            if slice_index < 0:
                return False

        self.pjs.curslice = slice_index
        self.pjs.imagedata = self.pjs.slices[self.pjs.curslice]
        self.pjs.timeSlider.setValue(slice_index+1)

        self.pjs.displayData()

        return True

    # Smallest possible value for firstSlice is 1.
    def cbFindSeeds(self, firstSlice: int = None, lastSlice: int = None, sigma: float = None, window_size: int = None,
                    bindilation: int = None, mindist: float = None, preview: bool = None, wait_for_thread: bool = False) -> bool:

        # If not enough parameters, open a dialog.
        if (firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None or
            window_size is False or window_size is None or sigma is False or sigma is None or bindilation is False or
            bindilation is None or mindist is False or mindist is None or preview is None) and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.findseeds.FindSeedsDialog(self.pjs)
            if self.pjs.n_frames == 1:
                lastSlice = 1
            else:
                lastSlice = self.pjs.slices.shape[0]

            ui.setupUi(dialog, firstslice=self.pjs.curslice + 1, lastslice=lastSlice,
                       gaussian_sigma=dialogs.findseeds.FindSeedsDialog.gaussianSigma,
                       winsz=dialogs.findseeds.FindSeedsDialog.window_size,
                       bindilation=dialogs.findseeds.FindSeedsDialog.binary_dilation_number,
                       mindist=dialogs.findseeds.FindSeedsDialog.min_distance_transform,
                       preview_flag=dialogs.findseeds.FindSeedsDialog.preview)

            # If you try to make this dialog non-modal, make sure to switch from dialog to using self.dialog.
            # Otherwise, when you delete the exec line and the method ends, there are no references to the
            # dialog object and it will disappear.
            # You will also need to comment out the dialog.close() below.
            dialog.exec_()
            dialog.show()

            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        # Otherwise, continue with the supplied parameters.
        else:
            theparameters = {'first': firstSlice, 'last': lastSlice, 'window_size': window_size, 'sigma': sigma,
                             'binary_dilation_number': bindilation,
                             'min_distance_transform': mindist, 'preview': preview}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Propagate forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Propagate backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO propagate!!
            """if run_in_thread:
                self.launch_thread(self.findSeeds, {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True}, finished_fn=self.finished_fn, progress_fn=self.progress_fn)
            else:
                self.findSeeds(theparameters, theslicenumbers)
                self.pjs.repaint()
            """

            self.launch_thread(self.findSeeds,
                               {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True},
                               finished_fn=self.finished_fn, progress_fn=self.progress_fn, wait_for_thread=wait_for_thread)

        return continue_flag

    def cbSegmentDetectedObjects(self, firstSlice: int = None, lastSlice: int = None, sigma: float = None, wait_for_thread: bool = False) -> bool:

        continue_flag: bool = False

        # If not enough parameters, open a dialog.
        if (firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None or
            sigma is False or sigma is None) and self.pjs is not None:

            firstSlice = self.pjs.curslice + 1

            if self.pjs.n_frames == 1:
                lastSlice = 1
            else:
                lastSlice = self.pjs.slices.shape[0]

            dialog = QtWidgets.QDialog()
            ui = dialogs.expandseeds.ExpandSeedsDialog()

            ui.setupUi(dialog, firstslice=firstSlice, lastslice=lastSlice,
                       gaussian_sigma=dialogs.expandseeds.ExpandSeedsDialog.gaussianSigma)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        # Otherwise, continue with the supplied parameters.
        else:
            theparameters = {'first': firstSlice, 'last': lastSlice, 'sigma': sigma}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Propagate forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Propagate backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO propagate!!
            """if run_in_thread:
                self.launch_thread(self.segmentROIs, {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True}, finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn)
            else:
                self.segmentROIs(theparameters, theslicenumbers)
                self.pjs.repaint()
            """
            self.launch_thread(self.segmentROIs,
                               {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True},
                               finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn,
                               wait_for_thread=wait_for_thread)

        return continue_flag

    # Smallest possible value for firstSlice is 1.
    def cbPropagateSeeds(self, firstSlice: int = None, lastSlice: int = None, xcorrWindowSize: int = None, wait_for_thread: bool = False) -> bool:

        # If not enough parameters, open a dialog.
        if (firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None or xcorrWindowSize is False or xcorrWindowSize is None) and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.propagateseeds.PropagateSeedsDialog()
            if self.pjs.n_frames == 1:
                lastSlice = 1
            else:
                lastSlice = self.pjs.slices.shape[0]

            ui.setupUi(dialog, firstslice=self.pjs.curslice + 1, lastslice=lastSlice,
                       xcorrwinsz=dialogs.propagateseeds.PropagateSeedsDialog.window_size)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        # Otherwise, continue with the supplied parameters.
        else:
            theparameters = {'first': firstSlice, 'last': lastSlice, 'xcorr_win_sz': xcorrWindowSize}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Propagate forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Propagate backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO propagate!!
            """if run_in_thread:
                self.launch_thread(self.propagateSeeds, {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True, 'stop': True}, finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn)
            else:
                self.propagateSeeds(theparameters, theslicenumbers)
                self.pjs.repaint()
            """
            self.launch_thread(self.propagateSeeds,
                               {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True,
                                'stop': True}, finished_fn=self.finished_fn, stop_fn=self.stop_fn,
                               progress_fn=self.progress_fn, wait_for_thread=wait_for_thread)

        return continue_flag

    # Smallest possible value for firstSlice is 1.
    def cbCentroidSeeds(self, firstSlice: int = None, lastSlice: int = None, wait_for_thread: bool = False) -> bool:

        # If not enough parameters, open a dialog.
        if (firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None) \
                and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.timepoints.TimePointsDialog()

            firstSlice = self.pjs.curslice + 1
            if self.pjs.n_frames == 1:
                lastSlice = 1
            else:
                lastSlice = self.pjs.slices.shape[0]

            ui.setupUi(dialog, firstslice=firstSlice, lastslice=lastSlice)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters_tuple = ui.parameters()
            theparameters = {'first': theparameters_tuple[0], 'last': theparameters_tuple[1]}

            dialog.close()

        # Otherwise, continue with the supplied parameters.
        else:
            theparameters = {'first': firstSlice, 'last': lastSlice}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Propagate forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Propagate backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO propagate!!
            """if run_in_thread:
                self.launch_thread(self.centroidSeeds,
                                   {'theslices': theslicenumbers, 'progress': True},
                                   finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn)
            else:
                self.centroidSeeds(theslicenumbers)
                self.pjs.repaint()
            """
            self.launch_thread(self.centroidSeeds,
                               {'theslices': theslicenumbers, 'progress': True},
                               finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn,
                               wait_for_thread=wait_for_thread)

        return continue_flag

    def cbExpandSeeds(self, firstSlice: int = None, lastSlice: int = None, sigma: float = None, wait_for_thread: bool = False) -> bool:

        # If not enough parameters, open a dialog.
        if (
                firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None or sigma is False or sigma is None) and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.expandseeds.ExpandSeedsDialog()

            firstSlice = self.pjs.curslice + 1

            if self.pjs.n_frames == 1:
                lastSlice = 1
            else:
                lastSlice = self.pjs.slices.shape[0]

            ui.setupUi(dialog, firstslice=firstSlice, lastslice=lastSlice,
                       gaussian_sigma=dialogs.expandseeds.ExpandSeedsDialog.gaussianSigma)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        # Otherwise, continue with the supplied parameters.
        else:
            theparameters = {'first': firstSlice, 'last': lastSlice, 'sigma': sigma}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Expand forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Expand backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO expand!!
            """if run_in_thread:
                self.launch_thread(self.expandSeeds,
                                   {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True},
                                   finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn)
            else:
                self.expandSeeds(theparameters, theslicenumbers)
                self.pjs.repaint()
            """
            self.launch_thread(self.expandSeeds,
                               {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True},
                               finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn,
                               wait_for_thread=wait_for_thread)

        return continue_flag

    def cbExpandNPropagateSeeds(self, firstSlice: int = None, lastSlice: int = None, sigma: float = None,
                                xcorrWindowSize: int = None, wait_for_thread: bool = False) -> bool:
        # If not enough parameters, open a dialog.
        if (firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None
            or xcorrWindowSize is False or xcorrWindowSize is None or sigma is False or sigma is None) \
                and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.expandnpropagateseeds.ExpandNPropagateSeedsDialog()
            if self.pjs.n_frames == 1:
                lastSlice = 1
            else:
                lastSlice = self.pjs.slices.shape[0]

            ui.setupUi(dialog, firstslice=self.pjs.curslice + 1, lastslice=lastSlice,
                       gaussian_sigma=dialogs.expandnpropagateseeds.ExpandNPropagateSeedsDialog.gaussianSigma,
                       xcorrwinsz=dialogs.expandnpropagateseeds.ExpandNPropagateSeedsDialog.window_size)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        # Otherwise, continue with the supplied parameters.
        else:
            theparameters = {'first': firstSlice, 'last': lastSlice, 'sigma': sigma, 'xcorr_win_sz': xcorrWindowSize}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Expand forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Expand backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO expand!!
            """if wait_for_thread:
                self.launch_thread(self.expandNPropagateSeeds,
                                   {'parameters': theparameters, 'theslices': theslicenumbers,
                                    'progress': True, 'stop': True},
                                   finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn)
            else:
                self.expandNPropagateSeeds(theparameters, theslicenumbers)
                self.pjs.repaint()
            """

            self.launch_thread(self.expandNPropagateSeeds,
                               {'parameters': theparameters, 'theslices': theslicenumbers,
                                'progress': True, 'stop': True},
                               finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn,
                               wait_for_thread=wait_for_thread)

        return continue_flag

    def propagateSeeds(self, parameters: dict, theslices: numpy.ndarray, progress_signal: ThreadSignals = None, stop_signal: ThreadSignals = None) -> bool:

        # Output parameters.
        Xflow: numpy.ndarray = numpy.empty(0)
        Yflow: numpy.ndarray = numpy.empty(0)

        xcorr_win_sz = parameters.get('xcorr_win_sz', RCBImage.DEFAULT_WINDOW_SZ)

        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # Make sure there are fiducials to move.
        if len(self.pjs.fiducials[theslices[0]]) == 0:
            if stop_signal is not None:
                stop_signal.emit(f"Stopping at slice {theslices[0] + 1}: there are no fiducials to move there.")
            return False

        # For every slice ...
        for i in range(num_slices - 1):
            # Calculate the optic flow between consecutive images and interpolate at the fiducials.
            Xflow, Yflow, _, _ = rimutils.flow(self.pjs.slices[theslices[i]],
                                               self.pjs.slices[theslices[i + 1]],
                                               numpy.array(self.pjs.fiducials[theslices[i]]), xcorr_win_sz)

            # Shift the position of the fiducials in this slice by the flow ... In this case, the coordinates are
            # organized as [x, y], as they come from the fiducial list in PyJAMAS.
            destination_point_array = numpy.array(self.pjs.fiducials[theslices[i]])
            destination_point_array[:, 0] = numpy.int64(numpy.round(
                numpy.float64(destination_point_array[:, 0]) + Xflow))  # X coordinate.
            destination_point_array[:, 1] = numpy.int64(numpy.round(
                numpy.float64(destination_point_array[:, 1]) + Yflow))  # Y coordinate.

            # Here we should clip the fiducials at the ends so that seeds do not go beyond image margins.
            # ind2 = find(next_seeds(:, 1) < 0);
            # next_seeds(intersect(ind, ind2), 1) = 0;
            # ind2 = find(next_seeds(:, 1) >= ud.imsize(1));
            # next_seeds(intersect(ind, ind2), 1) = ud.imsize(1) - 1;
            # ind2 = find(next_seeds(:, 2) < 0);
            # next_seeds(intersect(ind, ind2), 2) = 0;
            # ind2 = find(next_seeds(:, 2) >= ud.imsize(2));
            # next_seeds(intersect(ind, ind2), 2) = ud.imsize(2) - 1;

            # ... before copying them onto the next slice.
            self.pjs.fiducials[theslices[i + 1]] = destination_point_array.tolist()

            # Only emit progress signal if doing more than one slice.
            if num_slices > 1 and progress_signal is not None:
                progress_signal.emit(int((100*(i+1))/(num_slices-1)))

        return True

    def centroidSeeds(self, theslices: numpy.ndarray, progress_signal: ThreadSignals = None) -> bool:

        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices):
            thepolylines = [RUtils.qpolygonf2polygon(one_polyline) for one_polyline in self.pjs.polylines[theslices[i]]]

            for one_polyline in thepolylines:
                polycentroid = one_polyline.centroid
                self.pjs.addFiducial(int(polycentroid.x), int(polycentroid.y), theslices[i], paint=False)

            # Only emit progress signal if doing more than one slice.
            if num_slices > 1 and progress_signal is not None:
                progress_signal.emit(int((100 * (i + 1)) / num_slices))

        return True

    def findSeeds(self, parameters, theslices, progress_signal: ThreadSignals = None) -> bool:
        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices):
            theimage = self.pjs.slices[theslices[i]].copy()
            theimage = skimage.filters.gaussian(theimage, parameters['sigma'], multichannel=False)
            # Expand the seeds in the image.
            # ADD WHEELS TO DIALOG FOR WINDOW_SIZE, OPENING/CLOSING SIZE, MIN_DT_VALUE
            seed_coordinates, _ = rimutils.find_seeds(theimage,
                                                      parameters.get('window_size', RCBImage.DEFAULT_WINDOW_SZ),
                                                      parameters.get('binary_dilation_number',
                                                                     RCBImage.DEFAULT_BINARY_DILATIONS),
                                                      parameters.get('min_distance_transform',
                                                                     RCBImage.DEFAULT_MINIMUM_DISTANCE_TRANSFORM),
                                                      )

            # Add the coordinates to the list of fiducials.
            for aSeed in seed_coordinates:
                self.pjs.addFiducial(aSeed[1], aSeed[0], theslices[i], paint=False)

            # Only emit progress signal if doing more than one slice.
            if num_slices > 1 and progress_signal is not None:
                progress_signal.emit(int((100 * (i + 1)) / num_slices))

        return True

    def segmentROIs(self, parameters, theslices, progress_signal: ThreadSignals = None) -> bool:
        """

        :param parameters:
        :param theslices:
        :return:
        """

        centre_seeds: bool = parameters.get('centre_seeds', True)

        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        one = numpy.uint(1)

        # For every slice ...
        for i in range(num_slices):
            theimage: numpy.ndarray = self.pjs.slices[theslices[i]].copy()

            theimage = skimage.filters.gaussian(theimage, parameters.get('sigma', 0), multichannel=False)

            therois = self.pjs.polylines[theslices[i]].copy()  # without this copy instruction, the loop below will also go through newly added (within the loop) polygons

            theindex = -1

            # For every ROI ...
            for aroi in therois:
                theindex += 1
                # This code borrowed from rcbcrop.cbCrop. Places a seed at the center of the bounding box.
                # Because most classifiers will "detect" objects using rectangles, this works well. here.
                if aroi != []:
                    minx, miny, maxx, maxy = aroi.boundingRect().getCoords()
                    minx, miny, maxx, maxy = numpy.uint((minx, miny, maxx, maxy))
                else:
                    continue

                roi_im: numpy.ndarray = theimage[miny:(maxy+one), minx:(maxx+one)]
                rows, columns = roi_im.shape
                corner_coords = numpy.asarray([[0, 0], [0, columns - 1], [rows - 1, columns - 1], [rows - 1, 0]],
                                              dtype=numpy.int16)  # in row, col

                # Find seeds only within the roi.
                if centre_seeds:
                    seed_coordinates = numpy.asarray([[(miny+maxy)/2 - miny, (minx+maxx)/2 - minx]], dtype=numpy.int16)
                else:
                    seed_coordinates, _ = rimutils.find_seeds(roi_im,
                                                              parameters.get('window_size', RCBImage.DEFAULT_WINDOW_SZ),
                                                              parameters.get('binary_dilation_number',
                                                                             RCBImage.DEFAULT_BINARY_DILATIONS),
                                                              parameters.get('min_distance_transform',
                                                                             RCBImage.DEFAULT_MINIMUM_DISTANCE_TRANSFORM),
                                                              )

                    # if more than one seed, keep only the central one.

                # Add the coordinates to the list of fiducials.
                for aSeed in seed_coordinates:
                    self.pjs.addFiducial(minx+aSeed[1], miny+aSeed[0], theslices[i], paint=False)


                # Find the dimmest corner of the image gradient to be used as background seed.
                roi_grad: numpy.ndarray = ndimage.gaussian_gradient_magnitude(roi_im, parameters['sigma'])
                ind: int = numpy.argmin(roi_grad[corner_coords[:, 0], corner_coords[:, 1]])

                theseeds: numpy.ndarray = numpy.vstack((corner_coords[ind, [1, 0]], seed_coordinates[:, [1, 0]]))

                # Expand the seeds on the gradient of the roi.
                # NOTE: the goal here is to have one background and one object seed. TYPICALLY, the binary masks
                # for each of the two labels will be the opposite of each other. But find_contours, used
                # in rimutils.waterseed to extract contours from binary images, will detect zero crossings, and thus
                # will return the same contour for both. So below, we will discard the first contour (the one
                # corresponding to the background seed).
                contour_list = rimutils.waterseed(roi_grad, theseeds)

                # Add the contours to the list of annotations.
                for aContour in contour_list[1:]:
                    for aPoint in aContour:
                        aPoint[0], aPoint[1] = aPoint[0] + minx, aPoint[1] + miny

                    self.pjs.replacePolyline(theindex, aContour, theslices[i], paint=False)

                # Only emit progress signal if doing more than one slice.
                if num_slices > 1 and progress_signal is not None:
                    progress_signal.emit(int((100 * (i + 1)) / num_slices))

        return True

    def expandSeeds(self, parameters, theslices, progress_signal: ThreadSignals = None) -> bool:
        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices):
            # Make sure there are fiducials to expand.
            if not self.pjs.fiducials[theslices[i]]:
                continue

            theimage = self.pjs.slices[theslices[i]].copy()
            theimage = skimage.filters.gaussian(theimage, parameters['sigma'], multichannel=False)
            # Expand the seeds in the image.
            contour_list = rimutils.waterseed(theimage, numpy.asarray(self.pjs.fiducials[theslices[i]]))
            # Or for gradient-based segmentation:
            # import skimage.filters
            # contour_list = rimutils.waterseed(skimage.filters.sobel(self.pjs.slices[theslices[i]]),
            #                                               numpy.asarray(self.pjs.fiducials[theslices[i]]))

            # Add the contours to the list of annotations.
            for aContour in contour_list:
                self.pjs.addPolyline(aContour, theslices[i], paint=False)

            # Only emit progress signal if doing more than one slice.
            if num_slices > 1 and progress_signal is not None:
                progress_signal.emit(int((100 * (i + 1)) / num_slices))

        return True

    def centerSeeds(self, distance, theslices, exclude_peripheral_seeds=False):
        """

        :param distance:
        :param theslices:
        :param exclude_peripheral_seeds: use the convex_hull?
        :return:
        """
        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices):
            thepolylines = [RUtils.qpolygonf2polygon(one_polyline) for one_polyline in self.pjs.polylines[theslices[i]]]

            # Find the concave hull for the fiducials
            if exclude_peripheral_seeds:
                fiducial_hull: numpy.ndarray = RUtils.concave_hull(numpy.asarray(self.pjs.fiducials[theslices[i]]),
                                                                   self.DEFAULT_ALPHA_CONCAVE_HULL)

                if fiducial_hull.size == 0:
                    fiducial_hull = ConvexHull(numpy.asarray(self.pjs.fiducials[theslices[i]]))
            # The problem is that polygons and fiducials are not stored in the same order. Aaaaarghh!
            # Or rather, they are in the same order, but the order is updated when polygons are deleted
            # after touching the edge?
            # An alternative is to find, for each fiducial, an enclosing polygon, and go from there.
            for idx_fiducial, one_fiducial in enumerate(self.pjs.fiducials[theslices[i]]):
                # If peripheral points must be excluded and this is one of them, then skip it.
                if exclude_peripheral_seeds and idx_fiducial in fiducial_hull:
                    continue

                oneShapelyFiducial = Point(one_fiducial)

                for one_polyline in thepolylines:
                    if one_polyline.contains(oneShapelyFiducial):
                        if oneShapelyFiducial.distance(one_polyline.exterior) < distance and \
                                RCBImage._MIN_CELL_AREA < one_polyline.area < RCBImage._MAX_CELL_AREA:
                            polycentroid = one_polyline.centroid
                            self.pjs.fiducials[theslices[i]][idx_fiducial][0] = int(polycentroid.x)
                            self.pjs.fiducials[theslices[i]][idx_fiducial][1] = int(polycentroid.y)

                        break

        return

    def expandNPropagateSeeds(self, parameters, theslices, progress_signal: ThreadSignals = None, stop_signal: ThreadSignals = None) -> bool:

        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices - 1):
            # Expand in the current time point.
            self.expandSeeds(parameters, theslices[i], progress_signal)

            # Center seeds.
            self.centerSeeds(RCBImage.CENTER_SEEDS_CLOSER_TO_THE_EDGE, theslices[i])

            # Propagate to the next time point.
            self.propagateSeeds(parameters, theslices[i:i + 2], progress_signal, stop_signal)

            if progress_signal is not None:
                progress_signal.emit(int((100 * (i + 1)) / num_slices))

        # Finally, expand in the last time point and center the seeds.
        self.expandSeeds(parameters, theslices[-1], progress_signal)

        # Center seeds.
        self.centerSeeds(RCBImage.CENTER_SEEDS_CLOSER_TO_THE_EDGE, theslices[-1])

        if progress_signal is not None:
            progress_signal.emit(int(100))

        return True


