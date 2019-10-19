from featurize_jupyterlab.core import Model, Option
from .unet import Unet

encoder_weights_collection = [('random', None), 'imagenet']
encoder_name_collection = ['resnet34', 'resnet50', 'resnet101']

class UNet(Model):
    """Unet is a fully convolution neural network for image semantic segmentation
    """
    encoder_name = Option(default='resnet34', type='collection', collection=encoder_name_collection)
    encoder_weights = Option(default='imagenet', type='collection', collection=encoder_weights_collection)
    class_number = Option(default=2, type='number', help='class number of mask')

    def __call__(self):
        return Unet(
            encoder_name=self.encoder_name,
            encoder_weights=self.encoder_weights,
            classes=self.class_number,
            activation=None
        )
