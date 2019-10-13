from __future__ import absolute_import
from __future__ import division

import tensorflow as tf

from .layers import avg_pool2d
from .layers import batch_norm
from .layers import conv2d
from .layers import convbn
from .layers import convbnrelu as conv
from .layers import sconv2d
from .layers import sconvbn
from .layers import sconvbnrelu as sconv
from .layers import fc
from .layers import max_pool2d
from .layers import l2

from .ops import *
from .utils import pad_info
from .utils import set_args
from .utils import var_scope


def __args0__(is_training):
    return [([avg_pool2d, max_pool2d], {'scope': 'pool'}),
            ([batch_norm], {'scale': True, 'is_training': is_training,
                            'epsilon': 1e-5, 'scope': 'bn'}),
            ([conv2d], {'padding': 'SAME', 'activation_fn': None,
                        'weights_regularizer': l2(2e-5), 'scope': 'conv'}),
            ([fc], {'activation_fn': None, 'weights_regularizer': l2(2e-5),
                    'scope': 'fc'}),
            ([sconv2d], {'padding': 'SAME', 'activation_fn': None,
                         'weights_regularizer': l2(2e-5),
                         'biases_initializer': None,
                         'scope': 'sconv'})]


def __args__(is_training):
    return [([avg_pool2d, max_pool2d], {'scope': 'pool'}),
            ([batch_norm], {'scale': True, 'is_training': is_training,
                            'epsilon': 1e-5, 'scope': 'bn'}),
            ([conv2d], {'padding': 'SAME', 'activation_fn': None,
                        'weights_regularizer': l2(2e-5),
                        'biases_initializer': None, 'scope': 'conv'}),
            ([fc], {'activation_fn': None, 'weights_regularizer': l2(2e-5),
                    'scope': 'fc'}),
            ([sconv2d], {'padding': 'SAME', 'activation_fn': None,
                         'weights_regularizer': l2(2e-5),
                         'biases_initializer': None,
                         'scope': 'sconv'})]


def tnet(x, stack_fn, is_training, classes, stem,
         scope=None, reuse=None):
    x = pad(x, pad_info(7), name='conv1/pad')
    x = conv(x, 64, 7, stride=2, padding='VALID', scope='conv1')
    x = pad(x, pad_info(3), name='pool1/pad')
    x = max_pool2d(x, 3, stride=2, padding='VALID', scope='pool1')
    x = stack_fn(x)
    if stem: return x
    x = reduce_mean(x, [1, 2], name='avgpool')
    x = fc(x, classes, scope='logits')
    x = softmax(x, name='probs')
    return x


def tnet2(x, filters, blocks, is_training, classes, stem,
          scope=None, reuse=None):
    x = pad(x, pad_info(7), name='conv1/pad')
    x = conv(x, 64, 7, stride=2, padding='VALID', scope='conv1')
    x = stack(x, filters[0], blocks[0], scope='conv2')
    x = stack(x, filters[1], blocks[1], scope='conv3')
    x = stack(x, filters[2], blocks[2], scope='conv4')
    x = stack(x, filters[3], blocks[3], scope='conv5')
    if stem: return x
    x = reduce_mean(x, [1, 2], name='avgpool')
    x = fc(x, classes, scope='logits')
    x = softmax(x, name='probs')
    return x


@var_scope('tnet20')
@set_args(__args0__)
def tnet20(x, is_training=False, classes=1000,
           stem=False, scope=None, reuse=None):
    def stack_fn(x):
        x = _stack(x, 64, 2, stride1=1, scope='conv2')
        x = _stack(x, 64, 3, scope='conv3')
        x = _stack(x, 64, 5, scope='conv4')
        x = _stack(x, 64, 2, scope='conv5')
        return x
    return tnet(x, stack_fn, is_training, classes, stem, scope, reuse)


@var_scope('tnet21')
@set_args(__args0__)
def tnet21(x, is_training=False, classes=1000,
           stem=False, scope=None, reuse=None):
    def stack_fn(x):
        x = _stack(x, 64, 2, stride1=1, scope='conv2')
        x = _stack(x, 64, 3, scope='conv3')
        x = _stack(x, 128, 5, scope='conv4')
        x = _stack(x, 128, 2, scope='conv5')
        return x
    return tnet(x, stack_fn, is_training, classes, stem, scope, reuse)


@var_scope('tnet22')
@set_args(__args0__)
def tnet22(x, is_training=False, classes=1000,
           stem=False, scope=None, reuse=None):
    def stack_fn(x):
        x = _stack(x, 64, 3, stride1=1, scope='conv2')
        x = _stack(x, 64, 3, scope='conv3')
        x = _stack(x, 64, 3, scope='conv4')
        x = _stack(x, 64, 3, scope='conv5')
        return x
    return tnet(x, stack_fn, is_training, classes, stem, scope, reuse)


@var_scope('tnet23')
@set_args(__args0__)
def tnet23(x, is_training=False, classes=1000,
           stem=False, scope=None, reuse=None):
    def stack_fn(x):
        x = _stack(x, 64, 3, stride1=1, scope='conv2')
        x = _stack(x, 64, 4, scope='conv3')
        x = _stack(x, 64, 5, scope='conv4')
        x = _stack(x, 64, 6, scope='conv5')
        return x
    return tnet(x, stack_fn, is_training, classes, stem, scope, reuse)


@var_scope('tnet24')
@set_args(__args0__)
def tnet24(x, is_training=False, classes=1000,
           stem=False, scope=None, reuse=None):
    def stack_fn(x):
        x = _stack(x, 64, 2, stride1=1, scope='conv2')
        x = _stack(x, 64, 3, scope='conv3')
        x = _stack(x, 64, 3, scope='conv4')
        x = _stack(x, 64, 4, scope='conv5')
        return x
    return tnet(x, stack_fn, is_training, classes, stem, scope, reuse)


@var_scope('tnet30')
@set_args(__args__)
def tnet30(x, is_training=False, classes=1000,
           stem=False, scope=None, reuse=None):
    return tnet2(x, [64, 64, 64, 64], [3, 4, 6, 3],
                 is_training, classes, stem, scope, reuse)


@var_scope('tnet31')
@set_args(__args__)
def tnet31(x, is_training=False, classes=1000,
           stem=False, scope=None, reuse=None):
    return tnet2(x, [64, 64, 128, 128], [3, 4, 6, 3],
                 is_training, classes, stem, scope, reuse)


@var_scope('tnet32')
@set_args(__args__)
def tnet32(x, is_training=False, classes=1000,
           stem=False, scope=None, reuse=None):
    return tnet2(x, [64, 64, 64, 64], [4, 4, 4, 4],
                 is_training, classes, stem, scope, reuse)


@var_scope('tnet33')
@set_args(__args__)
def tnet33(x, is_training=False, classes=1000,
           stem=False, scope=None, reuse=None):
    return tnet2(x, [64, 64, 64, 64], [4, 5, 6, 7],
                 is_training, classes, stem, scope, reuse)


@var_scope('tnet34')
@set_args(__args__)
def tnet34(x, is_training=False, classes=1000,
           stem=False, scope=None, reuse=None):
    return tnet2(x, [64, 64, 64, 64], [3, 4, 4, 5],
                 is_training, classes, stem, scope, reuse)


@var_scope('tnet50')
@set_args(__args0__)
def tnet50(x, is_training=False, classes=1000,
           stem=False, scope=None, reuse=None):
    def stack_fn(x):
        x = _stack(x, 64, 2, stride1=1, scope='conv2')
        x = _stack(x, 128, 3, scope='conv3')
        x = _stack(x, 256, 5, scope='conv4')
        x = _stack(x, 512, 2, scope='conv5')
        return x
    return tnet(x, stack_fn, is_training, classes, stem, scope, reuse)


@var_scope('stack')
def _stack(x, filters, blocks, stride1=2, scope=None):
    x = _reduction(x, filters, stride1, scope='block1')
    for i in range(blocks):
        x = _normal(x, filters, scope="block%d" % (i + 2))
    return x


@var_scope('normal')
def _normal(x, filters, kernel_size=3, scope=None):
    shortcut = x
    x = conv(x, filters, 1, scope='1')
    #x = conv(x, filters, kernel_size, scope='2')
    x = sconv(x, None, kernel_size, 1, scope='2')
    x = convbn(x, 4 * filters, 1, scope='3')
    return relu(shortcut + x, name='out')


@var_scope('reduction')
def _reduction(x, filters, stride=2, kernel_size=3, scope=None):
    shortcut = x
    x = conv(x, filters, 1, scope='1')
    x = pad(x, pad_info(kernel_size), name='2/pad')
    #x = conv(x, filters, kernel_size, stride=stride,
    #         padding='VALID', scope='2')
    x = sconv(x, None, kernel_size, 1, stride=stride,
              padding='VALID', scope='2')
    x = convbn(x, 4 * filters, 1, scope='3')
    shortcut = pad(shortcut, pad_info(kernel_size), name='0/pad')
    shortcut = avg_pool2d(shortcut, kernel_size, stride,
                          padding='VALID', scope='0/pool')
    shortcut = convbn(shortcut, 4 * filters, 1, scope='0')
    return relu(shortcut + x, name='out')


@var_scope('stack')
def stack(x, filters, blocks, scope=None):
    x = block(x, filters, 2, scope='reduction')
    for i in range(blocks):
        x = block(x, filters, 1, scope="normal%d" % (i + 1))
    return x


@var_scope('pool')
def pool(x, filters, stride, kernel_size, scope=None):
    x = pad(x, pad_info(kernel_size), name='0/pad')
    x = max_pool2d(x, kernel_size, stride, padding='VALID', scope='0')
    x = conv(x, filters, 1, scope='1')
    x = sconv2d(x, None, 1, 1, scope='2')
    return convbn(x, 4 * filters, 1, scope='3')


@var_scope('block')
def block(x, filters, stride, kernel_size=3, scope=None):
    if stride > 1:
        shortcut = pool(x, filters, stride, kernel_size, scope='shortcut')
    else:
        shortcut = x
    x = conv(x, filters, 1, scope='1')
    x = pad(x, pad_info(kernel_size), name='2/pad')
    x = sconv2d(x, None, kernel_size, 1, stride, padding='VALID', scope='2')
    x = convbn(x, 4 * filters, 1, scope='3')
    return relu(shortcut + x, name='out')


# Simple alias.
TNet20 = tnet20
TNet21 = tnet21
TNet22 = tnet22
TNet23 = tnet23
TNet24 = tnet24
TNet30 = tnet30
TNet31 = tnet31
TNet32 = tnet32
TNet33 = tnet33
TNet34 = tnet34
TNet50 = tnet50
