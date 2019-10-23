import cv2
import imutils


class AspectAwareResize:
    def __init__(self, height, width, inter=cv2.INTER_AREA):
        # store the target image width, height, and interpolation
        # method used when resizing
        self.width = width
        self.height = height
        self.inter = inter

    def preprocess(self, image):
        (h, w) = image.shape[:2]
        dw = 0
        dh = 0
        if w < h:
            image = imutils.resize(image, width=self.width, inter=self.inter)
            dh = int((image.shape[0] - self.height) / 2.0)
        else:
            image = imutils.resize(image, height=self.height, inter=self.inter)
            dw = int((image.shape[1] - self.width) / 2.0)
        (h, w) = image.shape[:2]
        image = image[dh:h - dh, dw:w - dw]

        return cv2.resize(image, (self.width, self.height),interpolation=self.inter)