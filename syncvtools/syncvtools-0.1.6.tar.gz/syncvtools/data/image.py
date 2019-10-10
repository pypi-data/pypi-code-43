import numpy as np

class ImgSize:
    def __init__(self, width: int, height: int, channels: int = None):
        self.width = width
        self.height = height
        self.channels = channels

    def as_tuple(self):
        if self.channels is not None:
            return self.width, self.height, self.channels
        else:
            return self.width, self.height



class Image:
    def __init__(self, img_np: np.ndarray, img_filename = None):
        #TODO need to be immutable
        self.img_np = img_np
        self.img_filename = img_filename
        self.img_size = ImgSize(width=self.img_np.shape[1], height=self.img_np.shape[0], channels=self.img_np.shape[2])

    def size(self):
        return self.img_np.shape



