from featurize_jupyterlab.core import dataflow, option
from featurize_jupyterlab.transform import DualImageTransformation
import cv2
#
# @dataflow('Image Resizer', 'Resize image to any shape')
# @option('size', help='Square size of the image')
# class ImageResizer(Processor):
#     def __init__(self, size):
#         self.size = size
#
#     def __call__(self, data):
#         return cv2.resize(data, self.size)
#
#
@dataflow('Horizontal Flip', 'Horizontal flip the image and relative targets(like masks) with a given probability')
@option('probability', help='Probability to flip the image', default=0.5)
class HorizontalFlip(DualImageTransformation):
    def __call__(self, column, size):
        # TODO: do flip
        pass
