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

import numpy
from PyQt5 import QtWidgets

import pyjamas.dialogs as dialogs
from pyjamas.pjsthreads import ThreadSignals
from pyjamas.rcallbacks.rcallback import RCallback
from pyjamas.rimage.rimclassifier.rimclassifier import rimclassifier
import pyjamas.rimage.rimclassifier.rimlr as rimlr
import pyjamas.rimage.rimclassifier.rimnn as rimnnn
import pyjamas.rimage.rimclassifier.rimsvm as rimsvm



class RCBClassifiers(RCallback):
    def cbCreateLR(self, parameters: dict = None, wait_for_thread: bool = False) -> bool:  # Handle IO errors.
        continue_flag = True

        if parameters is None or parameters is False:
            dialog = QtWidgets.QDialog()
            ui = dialogs.logregression.LRDialog()
            ui.setupUi(dialog)

            dialog.exec_()
            dialog.show()

            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            parameters = ui.parameters()

            dialog.close()

        if continue_flag:
            self.pjs.batch_classifier.image_classifier = rimlr.lr(parameters)
            self.launch_thread(self.pjs.batch_classifier.fit, {'stop': True}, finished_fn=self.finished_fn,
                               stop_fn=self.stop_fn, wait_for_thread=wait_for_thread)

            return True

        else:
            return False

    def cbCreateNNMLP(self, parameters: dict = None, wait_for_thread: bool = False) -> bool:  # Handle IO errors.
        continue_flag = True

        if parameters is None or parameters is False:
            dialog = QtWidgets.QDialog()
            ui = dialogs.nnmlp.NNMLPDialog()
            ui.setupUi(dialog)

            dialog.exec_()
            dialog.show()

            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            parameters = ui.parameters()

            dialog.close()

        if continue_flag:
            self.pjs.batch_classifier.image_classifier = rimnnn.nnmlp(parameters)
            self.launch_thread(self.pjs.batch_classifier.fit, {'stop': True}, finished_fn=self.finished_fn,
                               stop_fn=self.stop_fn, wait_for_thread=wait_for_thread)

            return True

        else:
            return False

    def cbCreateSVM(self, parameters: dict = None, wait_for_thread: bool = False) -> bool:  # Handle IO errors.
        continue_flag = True

        if parameters is None or parameters is False:
            dialog = QtWidgets.QDialog()
            ui = dialogs.svm.SVMDialog()
            ui.setupUi(dialog)

            dialog.exec_()
            dialog.show()

            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            parameters = ui.parameters()

            dialog.close()

        if continue_flag:
            self.pjs.batch_classifier.image_classifier = rimsvm.svm(parameters)
            self.launch_thread(self.pjs.batch_classifier.fit, {'stop': True}, finished_fn=self.finished_fn,
                               stop_fn=self.stop_fn, wait_for_thread=wait_for_thread)

            return True

        else:
            return False

    def cbApplyClassifier(self, firstSlice: int = None, lastSlice: int = None, wait_for_thread: bool = False) -> bool:  # Handle IO errors.
        if (firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None) and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.timepoints.TimePointsDialog()

            if self.pjs.n_frames == 1:
                lastSlice = 1
            else:
                lastSlice = self.pjs.slices.shape[0]

            ui.setupUi(dialog, firstslice=self.pjs.curslice + 1, lastslice=lastSlice)

            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            firstSlice, lastSlice = ui.parameters()

            dialog.close()
        else:
            continue_flag = True

        if continue_flag:
            if firstSlice <= lastSlice:
                theslicenumbers = numpy.arange(firstSlice - 1, lastSlice, dtype=int)
            else:
                theslicenumbers = numpy.arange(lastSlice - 1, firstSlice, dtype=int)

            self.launch_thread(self.apply_classifier, {'theslices': theslicenumbers, 'progress': True, 'stop': True},
                               finished_fn=self.finished_fn,  progress_fn=self.progress_fn, stop_fn=self.stop_fn,
                               wait_for_thread=wait_for_thread)

            return True
        else:
            return False

    def apply_classifier(self, theslices: numpy.ndarray, progress_signal: ThreadSignals, stop_signal: ThreadSignals) -> bool:
        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        if stop_signal is not None:
            stop_signal.emit("Applying classifier ...")

        self.pjs.batch_classifier.predict(self.pjs.slices, theslices, progress_signal)

        # For every slice ...
        for index in theslices:
            self.add_classifier_boxes(self.pjs.batch_classifier.box_arrays[index], index, False)

        return True

    def add_classifier_boxes(self, boxes: numpy.ndarray = None, slice_index: int = None, paint: bool = True) -> bool:  # The first slice_index should be 0.
        if boxes is None or boxes is False or boxes == []:
            return False

        if slice_index is None or slice_index is False:
            slice_index = self.pjs.curslice

        for aBox in boxes:
            # Boxes stored as [minrow, mincol, maxrow, maxcol]
            self.pjs.addPolyline([[aBox[1], aBox[0]], [aBox[3], aBox[0]], [aBox[3], aBox[2]],
                                  [aBox[1], aBox[2]]], slice_index, paint=paint)

        return True

    def cbNonMaxSuppression(self, parameters: dict = None, first_tp: int = None, last_tp: int = None) -> bool:  # Handle IO errors.
        continue_flag = True

        if parameters is None or parameters is False:
            dialog = QtWidgets.QDialog()
            ui = dialogs.nonmax_suppr.NonMaxDialog(self.pjs)
            ui.setupUi(dialog)
            dialog.exec_()
            dialog.show()

            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted

            if continue_flag:
                parameters = ui.parameters()

            dialog.close()

        if continue_flag:
            if (first_tp is None or first_tp is False) and (last_tp is None or last_tp is False):
                dialog = QtWidgets.QDialog()
                ui = dialogs.timepoints.TimePointsDialog()
                ui.setupUi(dialog, dialogs.timepoints.TimePointsDialog.firstSlice,
                           dialogs.timepoints.TimePointsDialog.lastSlice)

                dialog.exec_()
                dialog.show()

                continue_flag = dialog.result() == QtWidgets.QDialog.Accepted

                if continue_flag:
                    first_tp, last_tp = ui.parameters()

                dialog.close()

            if first_tp <= last_tp:
                theslicenumbers = numpy.arange(first_tp - 1, last_tp, dtype=int)
            else:
                theslicenumbers = numpy.arange(last_tp - 1, first_tp, dtype=int)

            self.pjs.batch_classifier.non_max_suppression(
                parameters.get('prob_threshold', rimclassifier.DEFAULT_PROB_THRESHOLD),
                parameters.get('iou_threshold', rimclassifier.DEFAULT_IOU_THRESHOLD),
                parameters.get('max_num_objects', rimclassifier.DEFAULT_MAX_NUM_OBJECTS),
                theslicenumbers
            )

            for index in theslicenumbers:
                self.pjs.annotations.cbDeleteCurrentAnn(index)
                self.pjs.classifiers.add_classifier_boxes(self.pjs.batch_classifier.box_arrays[index][self.pjs.batch_classifier.good_box_indices[index]], index, True)

            self.pjs.repaint()

            return True

        else:
            return False


