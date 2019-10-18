"""
Module managing the validation screenshots.
"""
import logging as log
import time
import io
from tempfile import gettempdir

import pyautogui
import numpy
import PIL
from PIL.Image import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QBuffer, QByteArray, qCompress, qUncompress
import cv2

def pixmap_to_base64(image):
    '''
    :type image: QPixmap
    :return: bytes
    '''
    if not image:
        log.error('Not an image')
        return None

    data = QByteArray()
    buf = QBuffer(data)
    image.save(buf, 'PNG')
    return qCompress(data).toBase64().data().decode('utf8')

def base64_to_pixmap(image):
    '''
    :type image: bytes
    :return: QPixmap
    '''
    img = QPixmap()
    if img.loadFromData(qUncompress(QByteArray.fromBase64(bytes(image, 'utf8'))), 'PNG'):
        return img

    log.error("Can't convert to image: %s", image)
    return None


class ImageConverter:
    """
    Class handling the different image formats used in the program:
      - QPixmap: used to display in the interface
      - numpy.ndarray (OpenCV): to compute differences between images
      - PIL.Image: format in which the screenshots are taken
    The constructor takes one of the three supported image formats,
    automatically detects which format is used, and converts it in the two
    others.
    """
    def __init__(self, image):
        self.pixmap = None
        self.opencv = None
        self.pilimg = None

        self.set_image(image)

    def set_image(self, image):
        if image is None:
            raise "Can't convert null image"

        if isinstance(image, Image):
            self.pilimg = image
            self._pil_to_opencv()
            self._pil_to_pixmap()
        elif isinstance(image, QPixmap):
            self.pixmap = image
            self._pixmap_to_pil()
            self._pil_to_opencv()
        elif isinstance(image, numpy.ndarray):
            self.opencv = image
            self._opencv_to_pil()
            self._pil_to_pixmap()
        else:
            raise "Unsupported image format: {}".format(type(image))

    def _pil_to_opencv(self):
        img = numpy.array(self.pilimg)
        self.opencv = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    def _opencv_to_pil(self):
        img = cv2.cvtColor(self.opencv, cv2.COLOR_BGR2RGB)
        self.pilimg = PIL.Image.fromarray(img)

    def _pil_to_pixmap(self):
        self.pixmap = QPixmap.fromImage(ImageQt(self.pilimg).copy())

    def _pixmap_to_pil(self):
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)
        self.pixmap.save(buffer, "PNG")
        self.pilimg = PIL.Image.open(io.BytesIO(buffer.data()))


class Screenshot:
    """
    Data relative to screenshots and test case.
    Contains an "original" image to be used as reference and a "result" image
    acting as the final result of the test, the size and coords of the capture.
    """
    def __init__(self, region=()):
        # PNG as base64
        self.image = None
        self.result = None

        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

        if region:
            self.x, self.y, self.w, self.h = region

    def region(self):
        """ Size and position of the screenshot """
        return (self.x, self.y, self.w, self.h)

    def do_capture(self):
        """ Performs screenshot at the location defined by region() """
        path = '{0}/capture-{1}.png'.format(gettempdir(), round(time.time()*1000))
        pyautogui.screenshot(path, region=(self.x, self.y, self.w, self.h))
        log.info('Capture performed')
        self.image = pixmap_to_base64(QPixmap(path))
        log.info('Capture converted')

    def as_image(self):
        """ :return: QPixmap of the snapshot """
        return base64_to_pixmap(self.image)
