from featurize_jupyterlab.core import model, option, metadata
from .unet import Unet

encoder_weights_collection = [('random', None), 'imagenet']
encoder_name_collection = ['resnet34', 'resnet50', 'resnet101']

@model('Unet', 'Unet is a fully convolution neural network for image semantic segmentation')
@option('encoder_name', help='encoder of the unet', default='resnet34', type='collection', collection=encoder_name_collection)
@option('encoder_weights', help='pretrained weights of encoder', default='imagenet', type='collection', collection=encoder_weights_collection)
@option('class_number', help='class number of mask', type='number')
def unet(encoder_name, encoder_weights, class_number):
    return Unet(
        encoder_name=encoder_name,
        encoder_weights=encoder_weights,
        classes=class_number,
        activation=None
    )
