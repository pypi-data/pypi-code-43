import torch.nn as nn

from cframe.models.clasification import *
from cframe.models.fixation import *
from cframe.models.loss import SymmetricLovaszLoss
from cframe.models.segment import *

MODEL_DICT = dict(
    munet=dict(name='munet',
               model=MultiUnet,
               config=dict(nblocks=5, in_planes=3, num_classes=1,
                           channels=[64, 128, 256, 512, 512])
               ),
    tiramisu=dict(name='tiramisu',
               model=FCDenseNet103,
               config=dict(n_classes=2)
               ),
    unet_resnet=dict(name='unet_resnet',
                 model=unet_resnet34_cbam_v0a,
                 config=dict()
                     ),
    se_densenet161=dict(name='se_densenet161',
                     model=se_densenet161,
                    config=dict(pretrained=True, num_classes=2)),
    se_densenet201=dict(name='se_densenet201',
                        model=se_densenet201,
                        config=dict(pretrained=True, num_classes=2))
)

LOSS_DICT = dict(
    ce=dict(name='ce',
            loss=nn.CrossEntropyLoss,
            config=dict(weight=None, size_average=None, ignore_index=-100,
                        reduce=None, reduction='mean'
                        )),
    mse=dict(name='mse',
             loss=nn.MSELoss,
             config=dict(size_average=None, reduce=None, reduction='mean')),
    kl=dict(name='kl',
            loss=nn.KLDivLoss,
            config=dict(size_average=None, reduce=None, reduction='mean')),

    SymmetricLovaszLoss=dict(name='SymmetricLovaszLoss',
                             loss=SymmetricLovaszLoss,
                             config=(dict(weight=None, size_average=True)))
)


model_name = MODEL_DICT.keys()
loss_name = LOSS_DICT.keys()


class ModelConfiger(object):
    @classmethod
    def get_model_names(cls):
        return model_name
    @classmethod
    def get_loss_names(cls):
        return loss_name
    @classmethod
    def get_model_config(cls, name):
        return MODEL_DICT[name]
    @classmethod
    def get_loss_config(cls, name):
        return LOSS_DICT[name]