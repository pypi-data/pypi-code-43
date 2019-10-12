import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math
from .blocks import ConvBnActivation3D, DecoderBlock3D, EncoderBlock3D, init_weights

class UNet(nn.Module):
    def __init__(self, filters: list, in_channels: int = 1, n_classes: int = 13, residual: bool = True, bn: bool = True,
                 activation: str = 'leakyrelu', activation_inplace: bool = True):
        super(UNet, self).__init__()

        self.filters = filters
        self.depth = len(filters)
        if self.depth < 2:
            raise ValueError('Not enough filters, check UNet init code')

        self.in_channels = in_channels
        self.n_classes = n_classes

        self.residual = residual
        self.bn = bn
        self.activation = activation
        self.activation_inplace = activation_inplace

        # down layers
        self.down = nn.ModuleList([EncoderBlock3D(in_channels, filters[0], residual=residual, bn=bn, activation=activation,
                                                  activation_inplace=activation_inplace)])
        for i in range(1, self.depth):
            self.down.append(EncoderBlock3D(filters[i-1], filters[i], residual=residual, bn=bn, activation=activation,
                                            activation_inplace=activation_inplace))

        # bottleneck layers
        self.center = nn.ModuleList([ConvBnActivation3D(filters[self.depth - 1], filters[self.depth - 1], bn=bn, activation=activation,
                                                        activation_inplace=activation_inplace)])

        # up layers
        self.up = nn.ModuleList()
        for i in range(self.depth - 1, 0, -1):
            self.up.append(DecoderBlock3D(filters[i], filters[i], filters[i - 1], bn=bn, activation=activation,
                           activation_inplace=activation_inplace))
        self.up.append(DecoderBlock3D(filters[0], filters[0], self.n_classes, bn=bn, activation=activation,
                                      activation_inplace=activation_inplace))
        self.up.append(nn.Conv3d(self.n_classes, self.n_classes, kernel_size=1, bias=True))

        # init
        init_weights(self, 'kaiming')

    def forward(self, x):

        skips = []
        for i in range(0, self.depth):
            x = self.down[i](x)
            skips.append(x)

        center = x
        for i in range(0, len(self.center)):
            center = self.center[i](center)

        x = center
        for i in range(0, self.depth):
            x, _ = self.up[i](x, skips[self.depth - 1 - i])

        # output layer
        x = self.up[self.depth](x)

        return x
