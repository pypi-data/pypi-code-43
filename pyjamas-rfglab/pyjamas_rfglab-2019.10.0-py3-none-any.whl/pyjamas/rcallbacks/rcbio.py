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

import gzip
import os
import pickle

import cv2
import numpy
from PyQt5 import QtWidgets, QtGui, QtCore
import scipy.io
from sklearn.linear_model.logistic import LogisticRegression
from sklearn.svm.classes import SVC

from pyjamas.external import pascal_voc_io
from pyjamas.pjscore import PyJAMAS
from pyjamas.rcallbacks.rcallback import RCallback
from pyjamas.rimage.rimclassifier.rimclassifier import rimclassifier
from pyjamas.rimage.rimcore import rimage
from pyjamas.rimage.rimutils import rimutils
from pyjamas.rimage.rimclassifier.rimlr import lr
from pyjamas.rimage.rimclassifier.rimsvm import svm
from pyjamas.rimage.rimclassifier.rimnn import nnmlp
from pyjamas.rml.rneuralnetmlp import RNeuralNetMLP


class RCBIO(RCallback):
    FILENAME_BASE = "cell_"
    FILENAME_FIDUCIAL_LENGTH = 5

    def cbLoadTimeSeries(self, filename: str = None) -> bool:  # function cancel = cbLoadTimeSeries(fig, filename, in)
        """
        Loads a grayscale, multi-page TIFF.
        :param filename: file to open.
        :return: boolean (True if the image was loaded with no problems, False otherwise)
        """

        # Get file name.
        if filename is None or filename is False:
            fname = QtWidgets.QFileDialog.getOpenFileName(None, 'Load grayscale image ...', self.pjs.cwd,
                                                          filter='All files (*)')  # fname[0] is the full filename, fname[1] is the filter used.
            filename = fname[0]
            if filename == '':
                return False

        _, ext = os.path.splitext(filename)

        if ext not in rimage.image_extensions:
            self.pjs.statusbar.showMessage("That does not look like an image.")
            return False

        # Read image.
        self.pjs.slices = rimutils.read_stack(filename)

        # MISSING: error checking.

        # Store current working directory.
        self.pjs.cwd = os.path.dirname(filename)  # Path of loaded image.
        self.pjs.filename = filename

        # Initialize image and display.
        self.pjs.initImage()

        return True

    def cbLoadArray(self, image: numpy.ndarray) -> bool:
        if image is False or image is None:
            return False

        self.pjs.slices = image

        self.pjs.filename = 'animage'

        self.pjs.initImage()

    def cbLoadAnnotations(self, filename: str = None, image_file: str = None) -> bool:  # Handle IO errors
        """

        :param filename:
        :param image_file: path to an image to be loaded with the annotation file. None if no image is to be loaded.
        '' to create a black image.
        :return:
        """

        # Get file name.
        if filename is None or filename is False or filename == '': # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            fname = QtWidgets.QFileDialog.getOpenFileName(None, 'Load classifier ...', self.pjs.cwd,
                                                          filter='PyJAMAS data (*' + PyJAMAS.data_extension + ')')  # fname[0] is the full filename, fname[1] is the filter used.
            filename = fname[0]
            if filename == '':
                return False

        # Open file name and read annotations.
        fh = None

        try:
            fh = gzip.open(filename, "rb")
            fiducials = pickle.load(fh)
            polyline_list = pickle.load(fh)

        except (IOError, OSError) as ex:
            if fh is not None:
                fh.close()

            print(ex)
            return False

        if image_file == '':  # Create a blank image.
            # Find maxx, maxy, and maxz, and create a numpy.ndarray with those dimensions + 1.
            maxz = len(fiducials)
            maxx = 0
            maxy = 0

            # Fiducials and polylines are stored as (x, y) coordinates.
            # numpy.ndarrays are created with (slices, rows, cols).
            for slice_fiducials in fiducials:
                for afiducial in slice_fiducials:
                    maxx = max(maxx, afiducial[0])
                    maxy = max(maxy, afiducial[1])

            for slice_polylines in polyline_list:
                for apolyline in slice_polylines:
                    for afiducial in apolyline:
                        maxx = max(maxx, afiducial[0])
                        maxy = max(maxy, afiducial[1])

            virtual_image = numpy.zeros((maxz, int(maxy+1), int(maxx+1)), dtype=int)
            self.pjs.io.cbLoadArray(virtual_image)

        elif image_file is not False and image_file is not None:
            self.pjs.io.cbLoadTimeSeries(image_file)

        self.pjs.fiducials = fiducials

        self.pjs.polylines = [[] for i in range(self.pjs.n_frames)]
        for i, theframepolylines in enumerate(polyline_list):
            for j, thepolyline in enumerate(theframepolylines):
                if thepolyline != [[]]:
                    self.pjs.polylines[i].append(QtGui.QPolygonF())
                    for thepoint in thepolyline:
                        self.pjs.polylines[i][-1].append(QtCore.QPointF(thepoint[0], thepoint[1]))

        self.pjs.repaint()

        # Modify current path.
        self.pjs.cwd = filename[0:filename.rfind(os.sep)]

        return True

    def cbSaveTimeSeries(self, filename: str = '') -> bool:  # function cancel = cbLoadTimeSeries(fig, filename, in)
        '''
        Save a grayscale, multi-page TIFF.
        :return: boolean (True if the image was loaded with no problems, False otherwise)
        '''

        # Get file name.
        if filename == '' or filename is False:
            fname: tuple = QtWidgets.QFileDialog.getSaveFileName(None, 'Save time series ...', self.pjs.cwd,
                                                          filter='TIFF files (*.tif *.tiff)')  # fname[0] is the full filename, fname[1] is the filter used.
            filename = fname[0]
            if filename == '':
                return False

        # Save image.
        rimutils.write_stack(filename, self.pjs.slices)
        self.pjs.statusbar.showMessage('Image saved: ' + filename)

        self.pjs.cwd = os.path.dirname(filename)  # Path of loaded image.
        self.pjs.filename = filename

        return True

    def cbSaveImage(self, filename: str = None, x_range: tuple = False, y_range: tuple = False, z_range: tuple = False) -> bool:  # function cancel = cbLoadTimeSeries(fig, filename, in)
        """

        :param filename: '' for automated naming based on coordinates. If not provided, a dialog will open.
        :param x_range: tuple containing the min and max X values to save. If False, take the coordinates of the first polygon.
        :param y_range: tuple containing the min and max Y values to save. If False, take the coordinates of the first polygon.
        :param z_range: tuple containing the min and max Z values to save. If False, use just the current Z.
        :return: True if the image was properly saved; False if the save cannot be completed.
        """

        # Check X, Y, and Z parameters or assign default values.
        if z_range is False:
            z_range = tuple([self.pjs.curslice, self.pjs.curslice+1])

        if x_range is False:
            thepolylines = self.pjs.polylines[self.pjs.curslice]
            if thepolylines != [] and thepolylines[0] != []:
                thepolyline = self.pjs.polylines[self.pjs.curslice][0].boundingRect()
                x_range = tuple([int(thepolyline.x()), int(thepolyline.x()+thepolyline.width()+1)])
            else:
                return False

        if y_range is False and thepolylines != [] and thepolylines[0] != []:
            thepolylines = self.pjs.polylines[self.pjs.curslice]
            if thepolylines != [] and thepolylines[0] != []:
                thepolyline = self.pjs.polylines[self.pjs.curslice][0].boundingRect()
                y_range = tuple([int(thepolyline.y()), int(thepolyline.y() + thepolyline.height() + 1)])
            else:
                return False

        # Get file name.
        if filename is None or filename is False:
            fname: tuple = QtWidgets.QFileDialog.getSaveFileName(None, 'Save time series ...', self.pjs.cwd,
                                                          filter='TIFF files (*.tif *.tiff)')  # fname[0] is the full filename, fname[1] is the filter used.
            filename = fname[0]
            if filename == '':
                return False

        elif filename == '':
            filename = self.pjs.filename + '_X' + str(x_range[0]) + '_' + str(x_range[1]-1) + '_Y' + str(y_range[0]) + \
                       '_' + str(y_range[1]-1) + '_Z' + str(z_range[0]) + '_' + str(z_range[1]-1) + '.tif'

        # Save image.
        rimutils.write_stack(filename,
                             self.pjs.slices[z_range[0]:z_range[1], y_range[0]:y_range[1], x_range[0]:x_range[1]])
        self.pjs.statusbar.showMessage('Image saved: ' + filename)

        self.pjs.cwd = os.path.dirname(filename)  # Path of loaded image.

        return True

    def cbSaveDisplay(self, filename: str = None) -> bool:
        """

        :param filename: '' for automated naming based on coordinates. If not provided, a dialog will open.
        :return: True if the display was properly saved; False if the save cannot be completed.
        """

        # Get file name.
        if filename is False or filename is None:
            fname: tuple = QtWidgets.QFileDialog.getSaveFileName(None, 'Save display ...', self.pjs.cwd,
                                                          filter='TIFF files (*.tif *.tiff)')  # fname[0] is the full filename, fname[1] is the filter used.
            filename = fname[0]
            if filename == '':
                return False

        elif filename == '':
            filename = self.pjs.filename

        # Save image.
        self.capture_display(filename)

        self.pjs.statusbar.showMessage('Display saved: ' + filename)

        self.pjs.cwd = os.path.dirname(filename)  # Path of loaded image.

        return True

    def cbExportMovie(self, filename: str = None) -> bool:
        """

        :param filename: '' for automated naming based on coordinates. If not provided, a dialog will open.
        :return: True if the display was properly saved; False if the save cannot be completed.
        """

        # Get file name.
        if filename is False or filename is None:
            fname: tuple = QtWidgets.QFileDialog.getSaveFileName(None, 'Export movie with annotations ...', self.pjs.cwd,
                                                          filter='AVI (*.avi)')  # fname[0] is the full filename, fname[1] is the filter used.
            filename = fname[0]
            if filename == '':
                return False

        elif filename == '':
            filename = self.pjs.filename

        # Save image.
        self.export_movie(filename)

        self.pjs.statusbar.showMessage('Movie exported: ' + filename)

        self.pjs.cwd = os.path.dirname(filename)  # Path of loaded image.

        return True

    def capture_display(self, filename: str = None) -> QtGui.QImage:

        #pix_map: QtGui.QPixmap = self.pjs.gView.grab(self.pjs.gView.sceneRect().toRect())
        #pix_map: QtGui.QPixmap = self.pjs.gView.grab(QRect(0, 0, int(self.pjs.width * self.pjs.zoom_factors[self.pjs.zoom_index]), int(self.pjs.height * self.pjs.zoom_factors[self.pjs.zoom_index])))
        #pix_map: QtGui.QPixmap = self.pjs.gView.grab()
        #pix_map = pix_map.scaled(pix_map.width(), pix_map.height())

        self.pjs.gScene.clearSelection()
        self.pjs.gScene.setSceneRect(self.pjs.gScene.itemsBoundingRect())
        image: QtGui.QImage = QtGui.QImage(self.pjs.gScene.sceneRect().size().toSize(), QtGui.QImage.Format_ARGB32)
        image.fill(QtCore.Qt.transparent)
        painter: QtGui.QPainter = QtGui.QPainter(image)
        self.pjs.gScene.render(painter)

        if filename and filename is not None and filename != '':
            image.save(filename)

        return image

    def export_movie(self, filename: str = None) -> list:
        curslice = self.pjs.curslice

        qimage_list = []

        for i in range(self.pjs.n_frames):
            self.pjs.image.cbGoTo(i)
            qimage_list.append(self.capture_display())


        self.pjs.image.cbGoTo(curslice)

        if filename and filename is not None and filename != '':
            fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
            out = cv2.VideoWriter(filename, fourcc, self.pjs.fps, (self.pjs.width, self.pjs.height))

            for i in range(self.pjs.n_frames):
                a = rimutils.qimage2ndarray(qimage_list[i])
                gray_3c = cv2.merge([a[:, :, 0], a[:, :, 1], a[:, :, 2]])
                out.write(gray_3c)

            out.release()

        return qimage_list

    def cbSaveAnnotations(self, filename: str = None, polylines: list = None, fiducials: list = None) -> bool:  # Handle IO errors.
        # Get file name.
        if filename is None or filename is False: # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            fname = QtWidgets.QFileDialog.getSaveFileName(None, 'Save annotations ...', self.pjs.cwd,
                                                          filter='PyJAMAS data (*' + PyJAMAS.data_extension + ')')  # fname[0] is the full filename, fname[1] is the filter used.

            # If cancel ...
            filename = fname[0]
            if filename == '':
                return False

        self.pjs.cwd = os.path.dirname(filename)

        if filename[-4:] != PyJAMAS.data_extension:
            filename = filename + PyJAMAS.data_extension

        if not polylines:
            polylines = self.pjs.polylines

        if not fiducials:
            fiducials = self.pjs.fiducials

        # Prepare polygons to be stored: pickle does not support QPolygonF, so we convert the polygons to a list.
        # We store the polygons as QPolygonF because QGraphicsScene does have an addPolygon method that takes a
        # QPolygonF as the parameter.
        polyline_list = [[] for iframe in polylines]
        for iframe, theframepolylines in enumerate(polylines):
            for ipoly, thepolyline in enumerate(theframepolylines):
                polyline_list[iframe].append([])
                for ipnt, thepoint in enumerate(thepolyline):
                    polyline_list[iframe][ipoly].append([thepoint.x(), thepoint.y()])

        # Open file for writing.
        fh = None

        try:
            fh = gzip.open(filename, "wb")
            pickle.dump(fiducials, fh, pickle.HIGHEST_PROTOCOL)
            pickle.dump(polyline_list, fh, pickle.HIGHEST_PROTOCOL)

        except (IOError, OSError) as ex:
            if fh is not None:
                fh.close()

            print(ex)
            return False

        self.pjs.statusbar.showMessage(f"Saved {filename}.")

        return True

    def cbSaveAnnotationsXML(self, filename: str = None) -> bool:  # Handle IO errors.
        # Get file name.
        if filename is None or filename is False:  # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            fname = QtWidgets.QFileDialog.getSaveFileName(None, 'Save annotations ...',
                                                          self.pjs.cwd,
                                                          filter='XML file (*' + pascal_voc_io.XML_EXT + ')')  # fname[0] is the full filename, fname[1] is the filter used.

            # If cancel ...
            filename = fname[0]
            if filename == '':
                return False

        self.pjs.cwd = os.path.dirname(filename)

        if filename[-4:] != pascal_voc_io.XML_EXT:
            filename = filename + pascal_voc_io.XML_EXT

        writer = pascal_voc_io.PascalVocWriter(os.path.split(self.pjs.cwd)[1], os.path.basename(self.pjs.filename),
                                               [self.pjs.height, self.pjs.width, 1], localImgPath=self.pjs.filename)
        writer.verified = False

        theframepolylines = self.pjs.polylines[self.pjs.curslice]
        for ipoly, thepolyline in enumerate(theframepolylines):
            points = []

            for ipnt, thepoint in enumerate(thepolyline):
                points.append([thepoint.x(), thepoint.y()])

            label = 'cell'
            difficult = 0
            bndbox = RCBIO.convertPoints2BndBox(points)

            writer.addBndBox(bndbox[0], bndbox[1], bndbox[2], bndbox[3], label, difficult)

        writer.save(targetFile=filename)

        return True

    @staticmethod
    def convertPoints2BndBox(points):
        '''
        Copied from the LabelFile class in labelImg.
        :param points: list of points
        :return: tuple containing the bounding box for the list of points with this
                format (int(xmin), int(ymin), int(xmax), int(ymax)).
        '''

        xmin = float('inf')
        ymin = float('inf')
        xmax = float('-inf')
        ymax = float('-inf')
        for p in points:
            x = p[0]
            y = p[1]
            xmin = min(x, xmin)
            ymin = min(y, ymin)
            xmax = max(x, xmax)
            ymax = max(y, ymax)

        # Martin Kersner, 2015/11/12
        # 0-valued coordinates of BB caused an error while
        # training faster-rcnn object detector.
        if xmin < 1:
            xmin = 1

        if ymin < 1:
            ymin = 1

        return (int(xmin), int(ymin), int(xmax), int(ymax))

    def cbSaveClassifier(self, filename: str = None, theclassifier: rimclassifier = None) -> bool:  # Handle IO errors.
        if theclassifier is None or theclassifier is False:
            if self.pjs.batch_classifier.image_classifier is None:
                return False
            else:
                theclassifier = self.pjs.batch_classifier.image_classifier

        # Get file name.
        if filename is None or filename is False: # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            fname = QtWidgets.QFileDialog.getSaveFileName(None, 'Save classifier ...', self.pjs.cwd,
                                                          filter='PyJAMAS classifier (*' + rimclassifier.CLASSIFIER_EXTENSION + ')')  # fname[0] is the full filename, fname[1] is the filter used.

            # If cancel ...
            filename = fname[0]
            if filename == '':
                return False

        if filename[-4:] != rimclassifier.CLASSIFIER_EXTENSION:
            filename = filename + rimclassifier.CLASSIFIER_EXTENSION

        self.pjs.cwd = os.path.dirname(filename)

        theclassifier.save_classifier(filename)

        self.pjs.statusbar.showMessage(f'Saved {filename}.')

        return True

    def cbLoadClassifier(self, filename: str = None) -> bool:  # Handle IO errors
        # Get file name.
        if filename is None or filename is False: # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            fname = QtWidgets.QFileDialog.getOpenFileName(None, 'Load classifier ...', self.pjs.cwd,
                                                          filter='PyJAMAS classifier (*' + rimclassifier.CLASSIFIER_EXTENSION + ')')  # fname[0] is the full filename, fname[1] is the filter used.
            filename = fname[0]
            if filename == '':
                return False

        # Open file name and read classifier.
        fh = None
        theparameters: dict = None

        try:
            fh = gzip.open(filename, "rb")
            theparameters = pickle.load(fh)

        except (IOError, OSError) as ex:
            if fh is not None:
                fh.close()

            print(ex)
            return False

        theclassifier = theparameters.get('classifier', None)

        if type(theclassifier) is SVC:
            self.pjs.batch_classifier.image_classifier = svm(theparameters)
        elif type(theclassifier) is LogisticRegression:
            self.pjs.batch_classifier.image_classifier = lr(theparameters)
        elif type(theclassifier) is RNeuralNetMLP:
            self.pjs.batch_classifier.image_classifier = nnmlp(theparameters)
        else:
            self.pjs.statusbar.showMessage(f"Wrong classifier type.")
            return False

        # Modify current path.
        self.pjs.cwd = filename[0:filename.rfind(os.sep)]

        self.pjs.statusbar.showMessage(f"Classifier {filename} loaded.")

        return True

    def cbExportPolylineAnnotations(self, folder_name: str = None) -> bool:
        if folder_name is not None and folder_name is not False:  # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            self.pjs.cwd = folder_name

        self.pjs.annotation_mode = PyJAMAS.export_fiducial_polyline
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

        return True

    def export_polyline_annotations(self, x: int, y: int) -> bool:
        # Make sure the fiducial is in the list.
        assert [x, y] in self.pjs.fiducials[self.pjs.curslice], "Fiducial not found!"

        # Identify the fiducial.
        fiducial_index: int = self.pjs.fiducials[self.pjs.curslice].index([x, y])

        # List of polygons and fiducials for new annotation file.
        fiducial_list: list = [[] for i in range(self.pjs.n_frames)]
        polyline_list: list = [[] for i in range(self.pjs.n_frames)]

        # In every image:
        for slice in range(self.pjs.n_frames):
            # If there are enough fiducials and any polylines.
            if self.pjs.fiducials[slice] and fiducial_index < len(self.pjs.fiducials[slice]) and self.pjs.polylines[slice]:
                # Store the fiducial.
                fiducial_list[slice].append(self.pjs.fiducials[slice][fiducial_index])

                # Find the first polygon that contains the fiducial and store it as well.
                thefiducial: list = self.pjs.fiducials[slice][fiducial_index]
                thepolylines: list = [one_polyline for one_polyline in self.pjs.polylines[slice]]

                for index_polyline, one_polyline in enumerate(thepolylines):
                    if one_polyline.containsPoint(QtCore.QPointF(thefiducial[0], thefiducial[1]), QtCore.Qt.OddEvenFill):
                        polyline_list[slice].append(self.pjs.polylines[slice][index_polyline])
                        break

        # Save new annotation file.
        filename: str = os.path.join(self.pjs.cwd, self.FILENAME_BASE + str(fiducial_index+1).zfill(self.FILENAME_FIDUCIAL_LENGTH))
        self.pjs.io.cbSaveAnnotations(filename, polyline_list, fiducial_list)

        return True

    def cbImportSIESTAAnnotations(self, filename: str = None, image_file: str = None) -> bool:
        # Get file name.
        if filename is None or filename is False:  # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            fname = QtWidgets.QFileDialog.getOpenFileName(None, 'Import SIESTA annotations ...', self.pjs.cwd,
                                                          filter='SIESTA annotations (*.mat)')  # fname[0] is the full filename, fname[1] is the filter used.
            filename = fname[0]
            if filename == '':
                return False

        # Open file name and read annotations.
        try:
            matlabVars = scipy.io.loadmat(filename, struct_as_record=False)
        except (IOError, OSError) as ex:
            print(ex)
            return False

        ud = matlabVars['ud'][0][0]

        fiducials = numpy.transpose(ud.rfiducials, [2, 0, 1])
        polyline_list = numpy.transpose(ud.rpolygons, [2, 0, 1])

        if image_file == '':  # Create a blank image.
            # Find maxx, maxy, and maxz, and create a numpy.ndarray with those dimensions + 1.
            maxz = len(fiducials)
            maxx = 0
            maxy = 0

            # Fiducials and polylines are stored as (x, y) coordinates.
            # numpy.ndarrays are created with (slices, rows, cols).
            for slice_fiducials in fiducials:
                for afiducial in slice_fiducials:
                    maxx = max(maxx, afiducial[0])
                    maxy = max(maxy, afiducial[1])

            for slice_polylines in polyline_list:
                for apolyline in slice_polylines:
                    # For some reason, loadmat puts the polygons within a list.
                    if len(apolyline) == 1:
                        for afiducial in apolyline[0]:
                            if len(afiducial) > 0:
                                maxx = max(maxx, afiducial[0])
                                maxy = max(maxy, afiducial[1])

            virtual_image = numpy.zeros((maxz, int(maxy + 1), int(maxx + 1)), dtype=int)
            self.pjs.io.cbLoadArray(virtual_image)

        elif image_file is not False and image_file is not None:
            self.pjs.io.cbLoadTimeSeries(image_file)

        self.pjs.fiducials = [[] for i in range(self.pjs.n_frames)]

        for slice_fiducials in fiducials:
            for afiducial in slice_fiducials:
                if afiducial[-1] >= 0:
                    self.pjs.addFiducial(int(afiducial[0]), int(afiducial[1]), int(afiducial[2]))

        self.pjs.polylines = [[] for i in range(self.pjs.n_frames)]

        for z, slice_polylines in enumerate(polyline_list):
            for apolyline in slice_polylines:
                # For some reason, loadmat puts the polygons within a list.
                if len(apolyline[0]) > 1:
                    self.pjs.addPolyline(apolyline[0].tolist(), z)

        self.pjs.repaint()

        # Modify current path.
        self.pjs.cwd = filename[0:filename.rfind(os.sep)]

        return True

    def cbExportSIESTAAnnotations(self, filename: str = None) -> bool:
        """
        See https://www.mathworks.com/help/matlab/matlab_external/handling-data-returned-from-python.html
        for details.

        Something important here is to send float arrays to Matlab, otherwise there are errors when
        SIESTA tries to conduct certain operations on the arrays.

        :param filename:
        :return:
        """

        # Get file name.
        if filename is None or filename is False:  # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            fname = QtWidgets.QFileDialog.getSaveFileName(None, 'Export SIESTA annotations ...',
                                                          self.pjs.cwd,
                                                          filter='SIESTA annotations (*.mat)')  # fname[0] is the full filename, fname[1] is the filter used.
            # If cancel ...
            filename = fname[0]
            if filename == '':
                return False

        # Find max number of fiducials and polygons in any frame.
        rnfiducials = numpy.zeros(self.pjs.n_frames, dtype=numpy.float)
        max_n_polylines = 0
        for iSlice, thefiducials in enumerate(self.pjs.fiducials):
            rnfiducials[iSlice] = len(thefiducials)
            if len(self.pjs.polylines[iSlice]) > max_n_polylines:
                max_n_polylines = len(self.pjs.polylines[iSlice])

        # Create the fiducial array to send to Matlab.
        max_n_fiducials = numpy.amax(rnfiducials)
        rfiducials = -1. * numpy.ones([numpy.int(max_n_fiducials), 3, self.pjs.n_frames], dtype=numpy.float)

        # rpolylines is a list, which in Matlab is a cell.
        # The right dimensions are (max_n_fiducials, 1, self.pjs.n_frames)
        # Need to add the singlet second dimensions. The order of the square brackets is critical here.
        rpolylines = [[[[] for iSlice in range(self.pjs.n_frames)]] for iPol in range(max_n_polylines)]

        for iSlice, thefiducials in enumerate(self.pjs.fiducials):
            if thefiducials:
                thefiducials_array = numpy.asarray(thefiducials, dtype=numpy.float)
                rfiducials[0:thefiducials_array.shape[0], 0:2, iSlice] = thefiducials_array
                rfiducials[0:thefiducials_array.shape[0], 2, iSlice] = numpy.float(iSlice)

            thepolylines = self.pjs.polylines[iSlice]

            if thepolylines:
                for iPoly, thePoly in enumerate(thepolylines):
                    theintpoly = [[numpy.float(pnt.x()), numpy.float(pnt.y())] for pnt in thePoly]

                    if theintpoly != []:
                        theintpoly.append(theintpoly[0])

                    rpolylines[iPoly][0][iSlice] = theintpoly

        imsize = [numpy.float(self.pjs.width), numpy.float(self.pjs.height), numpy.float(self.pjs.n_frames)]

        # Build dictionary with the variables. Dictionaries are converted to structs
        ud = {}
        ud['rfiducials'] = rfiducials
        ud['rpolygons'] = rpolylines
        ud['rnfiducials'] = rnfiducials
        ud['imsize'] = imsize

        # Open file name and save annotations.
        try:
            scipy.io.savemat(filename, {'ud': ud}, appendmat=True)
        except (IOError, OSError) as ex:
            print(ex)
            return False

        # Modify current path.
        self.pjs.cwd = os.path.dirname(filename)

        return True



