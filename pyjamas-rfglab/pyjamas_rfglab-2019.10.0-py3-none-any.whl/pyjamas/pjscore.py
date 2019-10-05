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

from functools import partial
import os
import sys
from typing import List, Tuple

import numpy
from PyQt5 import QtCore, QtGui, QtWidgets
from skimage.measure import points_in_poly

from pyjamas.dragdropmainwindow import DragDropMainWindow
from pyjamas.rimage.rimclassifier.batchclassifier import BatchClassifier
import pyjamas.rimage.rimcore as rimcore
from pyjamas.rimage.rimutils import rimutils
from pyjamas.rutils import RUtils


class PyJAMAS(QtCore.QObject):
    '''
    PyJAMAS is Just A More Awesome Siesta.

    Uses calendar versioning (https://calver.org).
    Format: YYYY.M.minor

    YYYY - Full year - 2006, 2016, 2106
    M - Short month - 6, 16, 10
    minor - minor version number, starts at 0 for a given YYYY.M combination.


    PyJAMAS() creates a PyJAMAS user interface.

    '''

    # Logo path.
    logo_filename = 'pyjamas.tif'
    logo_folder = os.path.split(__file__)[0]
    logo_path = os.path.join(logo_folder, logo_filename)

    # Annotation modes.
    no_annotations: int = 0
    fiducials: int = 1
    rectangles: int = 2
    polylines: int = 3
    livewire: int = 4
    move_polyline: int = 5
    export_fiducial_polyline: int = 6
    delete_fiducials_outside_polyline: int = 7
    delete_fiducials_inside_polyline: int = 8
    copy_polyline: int = 9

    # Data file extension.
    data_extension: str = '.pjs'
    matlab_extension: str = '.mat'
    image_extensions: Tuple[str] = ('.tif', '.tiff', '.jpg')
    plugin_extension: str = '.py'

    # Plotting constants.
    fiducial_color = QtCore.Qt.red
    polyline_color = QtCore.Qt.green
    fiducial_radius: int = 6
    fiducial_brush_style: QtGui.QBrush = QtGui.QBrush()  # No fill for fiducials (open circles).
    polyline_brush_style: QtGui.QBrush = QtGui.QBrush()
    fiducial_font: QtGui.QFont = QtGui.QFont('Arial', 8)

    zoom_factors: tuple = (1., 2., 4., 8., .125, .25, .5)

    livewire_margin: int = 5

    # Calendar versioning: year.month.minor (+1 after you upload, this is always the current release number).
    __version__: str = '2019.10.0'

    def __init__(self):
        self.initData()  # Initialize object variables.
        self.setupUI()  # Build the GUI.

    def setupUI(self):
        self.app = QtWidgets.QApplication(sys.argv)

        import pyjamas.pjseventfilter as pjseventfilter
        import pyjamas.rcallbacks as rcallbacks

        QtCore.QObject.__init__(self)
        self.MainWindow = DragDropMainWindow()

        self.MainWindow.dropped.connect(self.file_dropped)

        self.MainWindow.setObjectName('PyJAMAS')
        self.MainWindow.resize(1183, 761)
        self.MainWindow.setWindowTitle('PyJAMAS')

        self.gScene = QtWidgets.QGraphicsScene(self.MainWindow)
        self.gScene.setSceneRect(0, 0, 1183, 761)
        self.gScene.setObjectName('gScene')

        self.gView = QtWidgets.QGraphicsView(self.gScene)
        self.gView.setObjectName('gView')
        self.gView.setMouseTracking(
            True)  # This here is necessary so that MouseMove events are triggered when no mouse buttons are pressed.
        self.filter = pjseventfilter.PJSEventFilter(self)
        self.gView.viewport().installEventFilter(self.filter)  # Capture mouse, but not keypress events.
        self.gView.installEventFilter(self.filter) # Captures key press events but not mouse ones.
        self.MainWindow.setCentralWidget(self.gView)

        self.timeSlider = QtWidgets.QSlider(self.MainWindow)
        self.timeSlider.setGeometry(QtCore.QRect(0, 0, 1183, 22))
        self.timeSlider.setOrientation(QtCore.Qt.Horizontal)
        self.timeSlider.setObjectName("timeSlider")

        self.menubar = QtWidgets.QMenuBar(self.MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1183, 22))
        self.menubar.setObjectName('menubar')
        self.menuIO = QtWidgets.QMenu(self.menubar)
        self.menuIO.setObjectName('menuIO')
        self.menuOptions = QtWidgets.QMenu(self.menubar)
        self.menuOptions.setObjectName('menuOptions')
        self.menuImage = QtWidgets.QMenu(self.menubar)
        self.menuImage.setObjectName('menuImage')
        self.menuClassifiers = QtWidgets.QMenu(self.menuImage)
        self.menuClassifiers.setObjectName('menuClassifiers')
        self.menuAnnotations = QtWidgets.QMenu(self.menubar)
        self.menuAnnotations.setObjectName('menuAnnotations')
        self.menuMeasurements = QtWidgets.QMenu(self.menubar)
        self.menuMeasurements.setObjectName('menuMeasurements')
        self.menuBatch = QtWidgets.QMenu(self.menubar)
        self.menuBatch.setObjectName('menuBatch')
        self.menuPlugins = QtWidgets.QMenu(self.menubar)
        self.menuPlugins.setObjectName('menuPlugins')
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName('menuHelp')
        self.MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(self.MainWindow)
        self.statusbar.setObjectName('statusbar')
        self.MainWindow.setStatusBar(self.statusbar)

        self.threadpool = QtCore.QThreadPool()
        #print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        # IO MENU ----------------------------------------------------------------------
        # Load image action
        self.io = rcallbacks.rcbio.RCBIO(self)

        self.addMenuItem(self.menuIO, 'Load grayscale image ...', QtCore.Qt.Key_T,
                         self.io.cbLoadTimeSeries)

        # Save time-lapse.
        self.addMenuItem(self.menuIO, 'Save grayscale image ...', QtCore.Qt.Key_S,
                         self.io.cbSaveTimeSeries)

        # Save time-lapse, but only ROI inside the polygon.
        self.addMenuItem(self.menuIO, 'Save grayscale image in polygon ...', QtCore.Qt.Key_U,
                         partial(self.io.cbSaveImage, filename=''))

        self.menuIO.addSeparator()

        # Load annotations.
        self.addMenuItem(self.menuIO, 'Load annotations ...', QtCore.Qt.SHIFT + QtCore.Qt.Key_L,
                         self.io.cbLoadAnnotations)

        # Save annotations.
        self.addMenuItem(self.menuIO, 'Save annotations ...', QtCore.Qt.Key_A,
                         self.io.cbSaveAnnotations)

        self.addMenuItem(self.menuIO, 'Export individual fiducial-polyline annotations ...', None,
                         self.io.cbExportPolylineAnnotations)

        self.menuIO.addSeparator()

        self.addMenuItem(self.menuIO, 'Load classifier ...', None,
                         self.io.cbLoadClassifier)

        self.addMenuItem(self.menuIO, 'Save current classifier ...', None,
                         self.io.cbSaveClassifier)

        self.menuIO.addSeparator()

        # Save XML roi (for TensorFlow training).
        self.addMenuItem(self.menuIO, 'Save XML ROI ...', QtCore.Qt.Key_X,
                         self.io.cbSaveAnnotationsXML)

        self.menuIO.addSeparator()

        # Import SIESTA annotations.
        self.addMenuItem(self.menuIO, 'Import SIESTA annotations ...', None,
                         self.io.cbImportSIESTAAnnotations)

        # Export SIESTA annotations.
        self.addMenuItem(self.menuIO, 'Export SIESTA annotations ...', None,
                         self.io.cbExportSIESTAAnnotations)

        self.menuIO.addSeparator()

        # Save display.
        self.addMenuItem(self.menuIO, 'Save display ...', None, self.io.cbSaveDisplay)

        # Save annotations movie.
        self.addMenuItem(self.menuIO, 'Export movie with annotations ...', None, self.io.cbExportMovie)

        self.menubar.addMenu(self.menuIO)

        # OPTIONS MENU ----------------------------------------------------------------------
        # Set brush size.
        self.options = rcallbacks.rcboptions.RCBOptions(self)

        self.addMenuItem(self.menuOptions, 'Set brush size ...', QtCore.Qt.Key_B,
                         self.options.cbSetBrushSize)

        self.addMenuItem(self.menuOptions, 'Display fiducial and polyline ids', QtCore.Qt.Key_I,
                         self.options.cbDisplayFiducialIDs)

        self.addMenuItem(self.menuOptions, 'Set frames per sec ...', None,
                         self.options.cbFramesPerSec)

        self.addMenuItem(self.menuOptions, 'Set working folder ...', None, self.options.cbSetCWD)

        self.menubar.addMenu(self.menuOptions)

        # IMAGE MENU ----------------------------------------------------------------------
        self.image = rcallbacks.rcbimage.RCBImage(self)
        # Adjust contrast
        self.addMenuItem(self.menuImage, 'Adjust contrast ...', QtCore.Qt.SHIFT + QtCore.Qt.Key_C, self.image.cbAdjustContrast)

        self.menuImage.addSeparator()

        # Rotate image CW.
        self.addMenuItem(self.menuImage, 'Play sequence', QtCore.Qt.Key_Backslash, self.image.cbPlay)

        self.menuImage.addSeparator()

        self.addMenuItem(self.menuImage, 'Rotate 90 degree clockwise', QtCore.Qt.SHIFT + QtCore.Qt.Key_Right,
                         partial(self.image.cbRotateImage,
                                 direction=rcallbacks.rcbimage.RCBImage.CW))

        # Rotate image CCW.
        self.addMenuItem(self.menuImage, 'Rotate 90 degree counter-clockwise', QtCore.Qt.SHIFT + QtCore.Qt.Key_Left,
                         partial(self.image.cbRotateImage,
                                 direction=rcallbacks.rcbimage.RCBImage.CCW))

        # Flip left-right.
        self.addMenuItem(self.menuImage, 'Flip left-right', QtCore.Qt.AltModifier + QtCore.Qt.Key_Right,
                         partial(self.image.cbFlipImage,
                                 direction=rcallbacks.rcbimage.RCBImage.LEFT_RIGHT))

        # Flip top-bottom.
        self.addMenuItem(self.menuImage, 'Flip up-down', QtCore.Qt.AltModifier + QtCore.Qt.Key_Up,
                         partial(self.image.cbFlipImage,
                                 direction=rcallbacks.rcbimage.RCBImage.UP_DOWN))

        self.menuImage.addSeparator()

        # Invert image.
        self.addMenuItem(self.menuImage, 'Invert image', None, self.image.cbInvertImage)

        # Maximum intensity projection.
        self.addMenuItem(self.menuImage, 'Maximum intensity projection', None, self.image.cbMIPImage)

        self.menuImage.addSeparator()

        self.addMenuItem(self.menuImage, 'Register image', QtCore.Qt.SHIFT + QtCore.Qt.Key_R, self.image.cbRegisterImage)

        self.menuImage.addSeparator()
        # Zoom action.
        self.addMenuItem(self.menuImage, 'Zoom', QtCore.Qt.Key_Z, self.image.cbZoom)

        # Crop action.
        self.addMenuItem(self.menuImage, 'Crop', QtCore.Qt.SHIFT + QtCore.Qt.Key_P, self.image.cbCrop)

        self.addMenuItem(self.menuImage, 'Kymograph', None, self.image.cbKymograph)

        self.menuImage.addSeparator()

        # Find seeds.
        self.addMenuItem(self.menuImage, 'Find seeds ...', QtCore.Qt.SHIFT + QtCore.Qt.Key_S,
                         self.image.cbFindSeeds)

        # Add fiducials in the centre of polylines.
        self.addMenuItem(self.menuImage, 'Add seeds in polyline centroids ...', None,
                         self.image.cbCentroidSeeds)

        # Propagate seeds.
        self.addMenuItem(self.menuImage, 'Propagate seeds ...', QtCore.Qt.SHIFT + QtCore.Qt.Key_E,
                         self.image.cbPropagateSeeds)

        # Expand seeds.
        self.addMenuItem(self.menuImage, 'Expand seeds ...', QtCore.Qt.SHIFT + QtCore.Qt.Key_X,
                         self.image.cbExpandSeeds)

        # Expand and propagate seeds.
        self.addMenuItem(self.menuImage, 'Expand and propagate seeds ...', QtCore.Qt.SHIFT + QtCore.Qt.Key_Z,
                         self.image.cbExpandNPropagateSeeds)

        # Classifiers.
        self.menuImage.addMenu(self.menuClassifiers)
        # -- Display Classifier: YellowBrick?
        self.classifiers = rcallbacks.rcbclassifiers.RCBClassifiers(self)
        self.addMenuItem(self.menuClassifiers, 'Create and train logistic regression model ...', None,
                         self.classifiers.cbCreateLR)
        self.addMenuItem(self.menuClassifiers, 'Create and train support vector machine ...', None,
                         self.classifiers.cbCreateSVM)
        self.addMenuItem(self.menuClassifiers, 'Create and train multilayer perceptron (simple neural net) ...', None,
                         self.classifiers.cbCreateNNMLP)

        # -- Decision Trees

        self.menuClassifiers.addSeparator()

        self.addMenuItem(self.menuClassifiers, 'Apply classifier ...', None, self.classifiers.cbApplyClassifier)

        self.menuClassifiers.addSeparator()

        self.addMenuItem(self.menuClassifiers, 'Non-maximum suppression ...', None,
                         self.classifiers.cbNonMaxSuppression)

        self.addMenuItem(self.menuClassifiers, 'Segment detected objects ...', None, self.image.cbSegmentDetectedObjects)

        self.menuImage.addSeparator()

        # Next image action
        self.addMenuItem(self.menuImage, 'Next frame', QtCore.Qt.Key_Period, self.image.cbNextFrame)

        # Previous image action
        self.addMenuItem(self.menuImage, 'Previous frame', QtCore.Qt.Key_Comma, self.image.cbPrevFrame)

        # Beginning and end actions
        self.addMenuItem(self.menuImage, 'Go to beginning', QtCore.Qt.Key_1, partial(self.image.cbGoTo, slice_index=0))
        self.addMenuItem(self.menuImage, 'Go to end', QtCore.Qt.Key_0, partial(self.image.cbGoTo, slice_index=-1))

        self.menubar.addMenu(self.menuImage)

        # Time slider
        self.timeSlider.valueChanged.connect(self.image.cbTimeSlider)


        # ANNOTATIONS MENU ----------------------------------------------------------------------
        # No annotations.
        self.annotations = rcallbacks.rcbannotations.RCBAnnotations(self)

        self.addMenuItem(self.menuAnnotations, 'No annotations', QtCore.Qt.Key_N, self.annotations.cbNoAnn)

        self.addMenuItem(self.menuAnnotations, 'Hide/display annotations', QtCore.Qt.Key_H, self.annotations.cbHideAnn)

        # Fiducials
        self.addMenuItem(self.menuAnnotations, 'Fiducials', QtCore.Qt.Key_F, self.annotations.cbFiducials)

        # Rectangles
        self.addMenuItem(self.menuAnnotations, 'Rectangles', QtCore.Qt.Key_R, self.annotations.cbRectangles)

        # Polylines
        self.addMenuItem(self.menuAnnotations, 'Polylines', QtCore.Qt.Key_Y, self.annotations.cbPolylines)

        # Livewire
        self.addMenuItem(self.menuAnnotations, 'LiveWire', QtCore.Qt.Key_W, self.annotations.cbLiveWire)

        self.menuAnnotations.addSeparator()

        # Copy and paste polyline
        self.addMenuItem(self.menuAnnotations, 'Copy polyline', QtCore.Qt.Key_C, self.annotations.cbCopyPolyline)

        self.addMenuItem(self.menuAnnotations, 'Paste polyline', QtCore.Qt.Key_V, self.annotations.cbPastePolyline)

        # Move polyline.
        self.addMenuItem(self.menuAnnotations, 'Move polyline', QtCore.Qt.Key_M, self.annotations.cbMovePolyline)

        self.menuAnnotations.addSeparator()

        self.addMenuItem(self.menuAnnotations, 'Track fiducials ...', QtCore.Qt.SHIFT + QtCore.Qt.Key_T,
                         self.annotations.cbTrackFiducials)

        self.menuAnnotations.addSeparator()

        # Delete annotations on the current image.
        self.addMenuItem(self.menuAnnotations, 'Delete all annotations on current frame', QtCore.Qt.Key_Minus,
                         self.annotations.cbDeleteCurrentAnn)

        # Delete ALL annotations.
        self.addMenuItem(self.menuAnnotations, 'Delete all annotations in the sequence', QtCore.Qt.Key_Underscore,
                         self.annotations.cbDeleteAllAnn)

        # Delete fiducials OUTSIDE polyline.
        self.addMenuItem(self.menuAnnotations, 'Delete fiducials outside polyline',
                         QtCore.Qt.SHIFT + QtCore.Qt.Key_O,
                         self.annotations.cbDeleteFiducialsOutsidePoly)

        self.menubar.addMenu(self.menuAnnotations)

        # Delete fiducials INSIDE polyline.
        self.addMenuItem(self.menuAnnotations, 'Delete fiducials inside polyline',
                         QtCore.Qt.SHIFT + QtCore.Qt.Key_I,
                         self.annotations.cbDeleteFiducialsInsidePoly)

        self.menubar.addMenu(self.menuAnnotations)

        # MEASUREMENTS MENU --------------------------------------------------------------------
        self.measurements = rcallbacks.rcbmeasure.RCBMeasure(self)

        self.addMenuItem(self.menuMeasurements, 'Measure polylines ...', None, self.measurements.cbMeasurePoly)

        self.menubar.addMenu(self.menuMeasurements)

        # BATCH MENU ---------------------------------------------------------------------------
        # Project and concatenate.
        self.batch = rcallbacks.rcbbatchprocess.RCBBatchProcess(self)
        self.addMenuItem(self.menuBatch, "Project and concatenate ...", None,
                         self.batch.cbBatchProjectConcat)

        self.menubar.addMenu(self.menuBatch)

        # PLUGINS MENU ---------------------------------------------------------------------------
        # Install plugin.
        self.plugins = rcallbacks.rcbplugins.RCBPlugins(self)
        self.addMenuItem(self.menuPlugins, "Install plugin ...", None,
                         self.plugins.cbInstallPlugin)

        self.menuPlugins.addSeparator()

        self.plugins.cbLoadPlugins()

        self.menubar.addMenu(self.menuPlugins)

        # HELP MENU ---------------------------------------------------------------------------
        # Project and concatenate.
        self.about = rcallbacks.rcbabout.RCBAbout(self)
        self.addMenuItem(self.menuHelp, "About", None,
                         self.about.cbAbout)

        self.menubar.addMenu(self.menuHelp)

        self.menubar.setNativeMenuBar(True)
        self.retranslateUi()

        # Init UI.
        self.io.cbLoadTimeSeries(PyJAMAS.logo_path)
        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)

        self.gView.show()
        self.MainWindow.show()


    def initData(self) -> bool:
        self._imageItem = None  # pixmap containing the image currently being displayed.
        self.zoom_index = 0  # index into PyJAMAS.zoom_factors to establish the zoom level.
        self.brush_size: int = 3  # brush size to paint polylines
        self.show_annotations: bool = True  # display or not annotations.
        self.display_fiducial_ids: bool = False  # display an identifier next to each fiducial
        self.fps: int = 7  # frames per second used to play the current sequence or when exporting as a movie.
        self.annotation_mode = PyJAMAS.no_annotations
        self.batch_classifier: BatchClassifier = None

        self.min_pix_percentile: int = 0  # Lowest percentile of the pixel values to map to display value 0.
        self.max_pix_percentile: int = 100  # Highest percentile of the pixel values to map to display value 255.

        self.cwd = os.getcwd()
        self.pjs_path, _ = os.path.split(os.path.realpath(__file__))

        self.plugin_list: List = []
        self.plugin_path: str = os.path.join(self.pjs_path, 'plugins')
        sys.path.append(self.plugin_path)

        self._poly_ = []  # Stores polyline coordinates while they are being drawn. Dunder (__a__) is reserved for special methods (e.g. __len__()).
        self._copied_poly_ = None  # Stores copied polyline to be pasted.
        self._agraphicsitem_ = None  # Stores a graphicsitem transiently (e.g. a rectangle as it is being dragged).

        return True

    def prepare_image(self):
        if hasattr(self, 'slices') and len(self.slices.shape) == 2:
            self.slices = numpy.expand_dims(self.slices, axis=0)

        self.curslice: int = 0
        self.imagedata: numpy.ndarray = self.slices[self.curslice]
        self.n_frames: int = self.slices.shape[0]
        self.height: int = self.slices.shape[1]  # number of rows.
        self.width: int = self.slices.shape[2]  # number of columns.
        self.min_pix_percentile = 0
        self.max_pix_percentile = 100

    def initImage(self):
        self.prepare_image()

        self.fiducials = [[] for i in range(self.n_frames)]
        self.polylines = [[] for i in range(self.n_frames)]

        # Make sure to continue to store the classifier in memory.
        if self.batch_classifier is not None:
            self.batch_classifier = BatchClassifier(self.n_frames, self.batch_classifier.image_classifier)
        else:
            self.batch_classifier = BatchClassifier(self.n_frames)

        # Resizing the window.
        self.gScene.setSceneRect(0, 0, self.width, self.height)
        self.MainWindow.resize(self.width * self.zoom_factors[self.zoom_index],
                               self.height * self.zoom_factors[self.zoom_index] + 60)
        self.timeSlider.setGeometry(QtCore.QRect(0, self.height + 18, self.MainWindow.width(), 22))

        self.timeSlider.valueChanged.disconnect()
        self.timeSlider.setMinimum(1)
        self.timeSlider.setMaximum(self.n_frames)
        self.timeSlider.setValue(1)
        self.timeSlider.valueChanged.connect(self.image.cbTimeSlider)

        self.displayData()


    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.menuIO.setTitle(_translate('PyJAMAS', 'IO'))
        self.menuOptions.setTitle(_translate('PyJAMAS', 'Options'))
        self.menuImage.setTitle(_translate('PyJAMAS', 'Image'))
        self.menuClassifiers.setTitle(_translate('PyJAMAS', 'Classifiers'))
        self.menuAnnotations.setTitle(_translate('PyJAMAS', 'Annotations'))
        self.menuMeasurements.setTitle(_translate('PyJAMAS', 'Measurements'))
        self.menuBatch.setTitle(_translate('PyJAMAS', 'Batch'))
        self.menuPlugins.setTitle(_translate('PyJAMAS', 'Plugins'))
        self.menuHelp.setTitle(_translate('PyJAMAS', 'Help'))

        return True

    def addMenuItem(self, themenu, theitemname, theshortcut, thecallbackfunction):
        newAction = QtWidgets.QAction(self.MainWindow)
        newAction.setEnabled(True)
        newAction.setText(theitemname)
        newAction.setIconText(theitemname)
        newAction.setToolTip(theitemname)
        newAction.setObjectName('action' + theitemname)
        newAction.triggered.connect(thecallbackfunction)

        if theshortcut is not None:
            newAction.setShortcut(theshortcut)

            # There are other possible values for the ShortcutContext in Qt.ShortcutContext. This is key for shortcuts to work when setNativeMenuBar(True) is used.
            newAction.setShortcutContext(QtCore.Qt.WidgetWithChildrenShortcut)
            newShortcut = QtWidgets.QShortcut(QtGui.QKeySequence(theshortcut),
                                              self.MainWindow)
            newShortcut.activated.connect(thecallbackfunction)

        themenu.addAction(newAction)

        return True

    def displayData(self):
        # Delete annotations from the screen.
        self.eraseAnnotations()

        # Stretch the dynamic range of the image and then convert to 8 bits.
        # There is an autocontrast function in pillow, but it only works on 8 bit grayscale or color data.
        # And converting to 8 bit and then doing the stretch leads to information loss and pixelated images.
        # img_16bit_to_8bit = RImage(self.imagedata).stretch()
        # img_16bit_to_8bit = numpy.array(img_16bit_to_8bit, dtype=numpy.uint8)

        # themin = numpy.min(self.imagedata)
        # themax = numpy.max(self.imagedata)

        # Now we stretch the image for display. I tested skimage.exposure.rescale_intensity and my own stretch method
        # (implemented  following the code in dipimage). stretch took 419 us, vs 484 us for rescale_intensity.
        # img_16bit_to_8bit = exposure.rescale_intensity(self.imagedata, in_range=(themin, themax), out_range=(0, 255))
        img_16bit_to_8bit = rimutils.stretch(self.imagedata, self.min_pix_percentile, self.max_pix_percentile)
        img_16bit_to_8bit = numpy.array(img_16bit_to_8bit, dtype=numpy.uint8)

        # Display image. The fourth parameter in the QImage constructor is 1*self.width for grayscale images,
        # and 3*self.width for color images.
        qImg = QtGui.QImage(bytes(img_16bit_to_8bit), self.width, self.height, self.width,
                            QtGui.QImage.Format_Grayscale8)
        pixmap = QtGui.QPixmap.fromImage(qImg)

        if self._imageItem is not None:
            self.gScene.removeItem(self._imageItem)

        self._imageItem = QtWidgets.QGraphicsPixmapItem(pixmap)
        self.gScene.addItem(self._imageItem)
        #self.gView.fitInView(self._imageItem, QtCore.Qt.KeepAspectRatio)

        if self.show_annotations:
            self.paintAnnotations()

        self.statusbar.showMessage(str(self.curslice + 1) + '/' + str(self.n_frames))

        return True

    # Perhaps create a class RAnnotations, and a PyJAMAS object has an RAnnotations property, that contains fields fiducials, polylines, etc. Does it contain the GraphicsScene as well? Yes, it is the argument to the constructor.
    # Add and remove methods take on an additional argument, the current slice. Constants are taken from class properties (PyJAMAS.fiducial_color, etc.).
    def addFiducial(self, x, y, z, paint=True):
        """

        :param x:
        :param y:
        :param z:
        :param paint: when set to False, the screen will not be repainted. This helps when adding fiducials on a different thread (which is not allowed to modify the GUI - see https://doc.qt.io/qt-5/thread-basics.html#gui-thread-and-worker-thread)
        :return:
        """
        self.fiducials[z].append([x, y])
        # print('Fiducials on frame ' + str(self.curslice) + ': ' + self.fiducials[self.curslice].__str__())

        # Add ellipse at (0,0). Then move it to the right position. This is important so that scenePos() returns the proper coordinates for the item.
        # If you add here directly in the (x, y) coordinates, scenePos() returns [0, 0].
        if paint and z == self.curslice:
            theItem = self.gScene.addEllipse(0, 0, PyJAMAS.fiducial_radius, PyJAMAS.fiducial_radius,
                                             PyJAMAS.fiducial_color,
                                             PyJAMAS.fiducial_brush_style)
            theItem.setPos(x - PyJAMAS.fiducial_radius / 2, y - PyJAMAS.fiducial_radius / 2)

            # If fiducial ids are on display, repaint them.
            if self.display_fiducial_ids:
                self.repaint()

        return True

    def findGraphicItem(self, x, y, class_type,
                        radius=fiducial_radius):  # Substitute in removeFiducial, removePolygon and movepolyline.
        theItems = self.gScene.items(
            QtCore.QRectF(x - radius / 4, y - radius / 4, radius / 2, radius / 2))

        # Because there are layers, if a rectangle was drawn on the ellipse, the rectangle will come first. So we look for the ellipse.
        for theClickedItem in theItems:
            if isinstance(theClickedItem, class_type):
                return theClickedItem

        return None

    def find_clicked_polyline(self, x: int, y: int) -> int:
        self._agraphicsitem_ = self.findGraphicItem(x, y, QtWidgets.QGraphicsPolygonItem)

        if isinstance(self._agraphicsitem_, QtWidgets.QGraphicsPolygonItem):
            theClickedPolygon = self._agraphicsitem_.polygon()

            try:
                index = self.polylines[self.curslice].index(theClickedPolygon)
            except LookupError:
                return -1
            else:
                self._poly_ = self.polylines[self.curslice][index]
                return index
        else:
            return -1

    def removeFiducial(self, x, y, z):
        # Grab items within a small square around the click point.
        """theItems = self.gScene.items(
            QtCore.QRectF(x - PyJAMAS.fiducial_radius / 4, y - PyJAMAS.fiducial_radius / 4, PyJAMAS.fiducial_radius / 2,
                          PyJAMAS.fiducial_radius / 2))

        # Because there are layers, if a rectangle was drawn on the ellipse, the rectangle will come first. So we look for the ellipse.
        for theClickedItem in theItems:
            if type(theClickedItem) == QtWidgets.QGraphicsEllipseItem:
                break
        """

        theClickedItem = self.findGraphicItem(x, y, QtWidgets.QGraphicsEllipseItem)

        # If you found an ellipse:
        if isinstance(theClickedItem, QtWidgets.QGraphicsEllipseItem):
            # Get coordinates. Find item in fiducial list. If you can find it, delete it there and delete the item from the scene.
            pos = theClickedItem.scenePos()
            deleteCoords = [int(pos.x() + PyJAMAS.fiducial_radius / 2), int(pos.y() + PyJAMAS.fiducial_radius / 2)]

            if deleteCoords in self.fiducials[z]:
                self.fiducials[z].remove(deleteCoords)
                self.gScene.removeItem(theClickedItem)
                # print('Fiducials on frame ' + str(self.curslice) + ': ' + self.fiducials[self.curslice].__str__())

                # If fiducial ids are on display, repaint them.
                if self.display_fiducial_ids:
                    self.repaint()

        return True

    def removeFiducialsPolyline(self, polyline: QtGui.QPolygonF = None, inside_flag: bool = True):
        # Go through the list of fiducials.
        polyline_list = RUtils.qpolygonf2ndarray(polyline)

        inside_poly_flags: numpy.ndarray = points_in_poly(self.fiducials[self.curslice], polyline_list)

        # To avoid deleting fiducials from the list we are checking.
        fiducial_list = self.fiducials[self.curslice].copy()

        for thefiducial, is_inside in zip(fiducial_list, inside_poly_flags):
            if (is_inside and inside_flag) or ((not is_inside) and (not inside_flag)):
                self.removeFiducial(thefiducial[0], thefiducial[1], self.curslice)

        return True

    def drawRectangle(self, x0, y0, x1, y1):
        # print([x0,y0].__str__() + " " + [x1, y1].__str__())
        if x0 > x1:
            x0, x1 = x1, x0

        if y0 > y1:
            y0, y1 = y1, y0

        # print([x0,y0].__str__() + " " + [x1, y1].__str__())
        pen = QtGui.QPen()
        pen.setWidth(self.brush_size)
        pen.setColor(PyJAMAS.polyline_color)

        # thepolyline = QtGui.QPolygonF()

        theItem = self.gScene.addRect(x0, y0, x1 - x0, y1 - y0, pen, PyJAMAS.polyline_brush_style)

        return theItem  # , thepolyline

    def drawPath(self, coordinates):
        thepolyline = QtGui.QPolygonF()

        for thepoint in coordinates:
            thepolyline.append(QtCore.QPointF(thepoint[0], thepoint[1]))

        thepath = QtGui.QPainterPath()
        thepath.addPolygon(thepolyline)

        pen = QtGui.QPen()
        pen.setWidth(self.brush_size)
        pen.setColor(PyJAMAS.polyline_color)

        theItem = self.gScene.addPath(thepath, pen, PyJAMAS.polyline_brush_style)

        return theItem, thepolyline

    def drawPolyline(self, aQPolygonF):
        pen = QtGui.QPen()
        pen.setWidth(self.brush_size)
        pen.setColor(PyJAMAS.polyline_color)

        theItem = self.gScene.addPolygon(aQPolygonF, pen, PyJAMAS.polyline_brush_style)

        return theItem

    def addPolyline(self, coordinates: list, z: int, paint: bool = True) -> bool:
        thepolyline = QtGui.QPolygonF()

        for thepoint in coordinates:
            thepolyline.append(QtCore.QPointF(thepoint[0], thepoint[1]))

        self.polylines[z].append(thepolyline)

        # Draw the polyline if it is being added to the right time point.
        if paint and z == self.curslice:
            self.drawPolyline(thepolyline)

            # If ids are on display, repaint them.
            if self.display_fiducial_ids:
                self.repaint()

        return True

    def replacePolyline(self, index: int, coordinates: list, z: int, paint: bool = True) -> bool:
        thepolyline = QtGui.QPolygonF()

        for thepoint in coordinates:
            thepolyline.append(QtCore.QPointF(thepoint[0], thepoint[1]))

        self.polylines[z][index] = thepolyline

        # Draw the polyline if it is being added to the right time point.
        if paint and z == self.curslice:
            self.drawPolyline(thepolyline)

            # If ids are on display, repaint them.
            if self.display_fiducial_ids:
                self.repaint()

        return True

    def removePolyline(self, x, y, z):
        # Grab items within a small square around the click point.
        """theItems = self.gScene.items(
            QtCore.QRectF(x - PyJAMAS.fiducial_radius / 4, y - PyJAMAS.fiducial_radius / 4, PyJAMAS.fiducial_radius / 2,
                          PyJAMAS.fiducial_radius / 2))

        # Because there are layers, if something was drawn on the polygon, that other thing will come first. So we look for the first polygon.
        for theClickedItem in theItems:
            if type(theClickedItem) == QtWidgets.QGraphicsPolygonItem:
                break
        """

        theClickedItem = self.findGraphicItem(x, y, QtWidgets.QGraphicsPolygonItem)

        # print("(" + theClickedItem.scenePos().x().__str__() + ", " + theClickedItem.scenePos().y().__str__() + ") " + theClickedItem.type().__str__())
        # If you clicked on a polyline (not only the edge, but anywhere inside as well):
        if isinstance(theClickedItem, QtWidgets.QGraphicsPolygonItem):
            theClickedPolygon = theClickedItem.polygon()

            try:
                index = self.polylines[z].index(theClickedPolygon)
            except LookupError:
                return False
            else:
                self.polylines[z].pop(index)
                self.gScene.removeItem(theClickedItem)

                # If ids are on display, repaint them.
                if self.display_fiducial_ids:
                    self.repaint()

                return True
        else:
            return False

    def eraseAnnotations(self):
        allItems = self.gScene.items()

        for i in allItems:
            if isinstance(i,
                          (QtWidgets.QGraphicsEllipseItem, QtWidgets.QGraphicsPolygonItem, QtWidgets.QGraphicsTextItem)
                          ):
                self.gScene.removeItem(i)

        return True

    def paintAnnotations(self):
        pen = QtGui.QPen()
        pen.setWidth(self.brush_size)
        pen.setColor(PyJAMAS.polyline_color)

        for i, thepoly in enumerate(self.polylines[self.curslice]):
            if thepoly == [] or list(thepoly) == []:
                continue

            self.gScene.addPolygon(thepoly, pen, PyJAMAS.polyline_brush_style)

            if self.display_fiducial_ids:
                polygon = RUtils.qpolygonf2polygon(thepoly)
                theItem = self.gScene.addText(str(i + 1), PyJAMAS.fiducial_font)
                theItem.setPos(polygon.centroid.x, polygon.centroid.y)
                theItem.setDefaultTextColor(self.polyline_color)

        # Paint fiducials after polylines so that polylines are in the foreground.
        for i, thefiducial in enumerate(self.fiducials[self.curslice]):
            # Add ellipse at (0,0). Then move it to the right position. This is important so that scenePos() returns the proper coordinates for the item.
            # If you add here directly in the (x, y) coordinates, scenePos() returns [0, 0].
            theItem = self.gScene.addEllipse(0, 0, self.fiducial_radius, self.fiducial_radius, self.fiducial_color,
                                             self.fiducial_brush_style)

            x = thefiducial[0]
            y = thefiducial[1]
            theItem.setPos(x - PyJAMAS.fiducial_radius / 2, y - PyJAMAS.fiducial_radius / 2)

            if self.display_fiducial_ids:
                theItem = self.gScene.addText(str(i + 1), PyJAMAS.fiducial_font)
                theItem.setPos(x - PyJAMAS.fiducial_radius / 2, y - PyJAMAS.fiducial_radius / 2)
                theItem.setDefaultTextColor(self.fiducial_color)

        # Make sure focus goes back to the main window.
        self.MainWindow.activateWindow()

        return True

    def repaint(self):
        self.eraseAnnotations()
        self.paintAnnotations()

        return True

    def file_dropped(self, l: list) -> bool:
        for file_name in l:
            if os.path.exists(file_name):
                file_name_str = str(file_name).lower()
                _, extension = os.path.splitext(file_name_str)

                if extension in rimcore.rimage.image_extensions:
                    self.io.cbLoadTimeSeries(file_name_str)
                elif extension == PyJAMAS.data_extension:
                    self.io.cbLoadAnnotations(file_name_str)
                elif extension == PyJAMAS.matlab_extension:
                    self.io.cbImportSIESTAAnnotations(file_name_str)

            else:
                return False

        return True

    @classmethod
    def new_pjs(cls, theimage: numpy.ndarray):
        thenewpjs: PyJAMAS = PyJAMAS()
        thenewpjs.io.cbLoadArray(theimage)

        return thenewpjs

    def __copy__(self):
        newone = type(self)()
        newone.__dict__.update(self.__dict__)
        return newone

    def __deepcopy__(self, memodict={}):
        newone = type(self)()
        memodict[id(self)] = newone

        # Deep copy methods with a __deepcopy__ magic method.
        # Otherwise, copy by reference.
        for k, v in self.__dict__.items():
            if getattr(v, "__deepcopy__", None):
                setattr(newone, k, v.__deepcopy__(memodict))
            else:
                setattr(newone, k, v)

        return newone


def main():
    #app = QtWidgets.QApplication(sys.argv)

    aPyJAMA: PyJAMAS = PyJAMAS()
    sys.exit(aPyJAMA.app.exec_())


if __name__ == '__main__':
    main()
