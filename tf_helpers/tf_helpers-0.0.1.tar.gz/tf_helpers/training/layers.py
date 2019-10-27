# -*- coding: utf-8 -*-

__author__ = """Larissa Triess"""
__email__ = 'mail@triess.eu'

import math

import tensorflow as tf


def get_padding_sizes(
        spacial_dimensions: tuple, kernel_size: tuple, strides: tuple, scope: str = None
):

    """
    Computes the padding sizes for a rank 4 tensor according to the `kernel_size` and `strides`
    of a 2D convolution with `same` padding. The computation is equivalent to TF implementation.

    Parameters:
        spacial_dimensions (tuple): A tuple of two integers corresponding to the spacial
            dimensions H and W of Tensor(shape=[N, H, W, C]).
        kernel_size (tuple): A tuple of two integers defining the kernel size of a
            convolution for which to compute the corresponding padding of the input tensor.
        strides (tuple): A tuple of two integers defining the strides of a
            convolution for which to compute the corresponding padding of the input tensor.
        scope (str): The name scope of the function.

    Returns:
        (int, int, int, int): Four integers corresponding to the padding at the top, bottom,
            left, and right, respectively.

    Raises:
        TypeError: When `spacial_dimensions`, `kernel_size`, or `strides` are not tuples of integers.
        ValueError: If `strides` is smaller than 1 or greater than the spacial dimension.
        ValueError: If `kernel_size` is smaller than 1 or greater than the spacial dimension.
    """

    if not (isinstance(spacial_dimensions, tuple) and all([isinstance(d, int) for d in spacial_dimensions])):
        raise TypeError('`spacial_dimensions` must be a tuple of two integers.')
    if not (isinstance(kernel_size, tuple) and all([isinstance(k, int) for k in kernel_size])):
        raise TypeError('`kernel_size` must be a tuple of two integers.')
    if not (isinstance(strides, tuple) and all([isinstance(s, int) for s in strides])):
        raise TypeError('`strides` must be a tuple of two integers.')
    if not all([1 <= s <= d for s, d in zip(strides, spacial_dimensions)]):
        raise ValueError('Strides cannot be smaller than 1 or greater than the corresponding '
                         'spacial dimension. I got {}.'.format(strides))
    if not all([1 <= k <= d for k, d in zip(kernel_size, spacial_dimensions)]):
        raise ValueError('Kernel size cannot be smaller than 1 or greater than the corresponding '
                         'spacial dimension. I got {} vs. {}.'.format(kernel_size, spacial_dimensions))

    with tf.name_scope(name=scope, default_name='calculate_padding_sizes'):
        # Compute the output height and width
        out_h = int(math.ceil(float(spacial_dimensions[0]) / float(strides[0])))
        out_w = int(math.ceil(float(spacial_dimensions[1]) / float(strides[1])))

        # Calculate the amount of padding per spacial dimension
        pad_h = max((out_h - 1) * strides[0] + kernel_size[0] - spacial_dimensions[0], 0)
        pad_w = max((out_w - 1) * strides[1] + kernel_size[1] - spacial_dimensions[1], 0)

        pad_top = pad_h // 2  # amount of padding on the top
        pad_bottom = pad_h - pad_top  # amount of padding on the bottom
        pad_left = pad_w // 2  # amount of padding on the left
        pad_right = pad_w - pad_left  # amount of padding on the right

    return pad_top, pad_bottom, pad_left, pad_right


def pad(tensor, paddings, mode='CONSTANT', constant_values=0, name=None):
    """Pads a tensor.

    This operation pads a `tensor` according to the `paddings` you specify.
    `paddings` is an integer tensor with shape `[n, 2]`, where n is the rank of
    `tensor`. For each dimension D of `input`, `paddings[D, 0]` indicates how
    many values to add before the contents of `tensor` in that dimension, and
    `paddings[D, 1]` indicates how many values to add after the contents of
    `tensor` in that dimension.

    The padded size of each dimension D of the output is:

    `paddings[D, 0] + tensor.dim_size(D) + paddings[D, 1]`

    For `mode` `CONSTANT`, `REFLECT`, and `SYMMETRIC` take a look at the TF documentation:
    https://www.tensorflow.org/api_docs/python/tf/pad

    If `mode` is "CYCLIC" then both `paddings[D, 0]` and `paddings[D, 1]` must be
    no greater than `tensor.dim_size(D)`.

    Example for `mode` `CYCLIC`:

    ```python
    t = tf.constant([[1, 2, 3], [4, 5, 6]])
    paddings = tf.constant([[0, 1], [2, 1]])
    tf.pad(t, paddings, "CYCLIC")  # [[2, 3, 1, 2, 3, 1],
                                   #  [5, 6, 4, 5, 6, 4],
                                   #  [2, 3, 1, 2, 3, 1]]
    ```

    Parameters:
        tensor: A `Tensor`.
        paddings: A `Tensor` of type `int32`.
        mode: One of "CONSTANT", "REFLECT", "SYMMETRIC", or "CYCLIC" (case-insensitive)
        name: A name for the operation (optional).
        constant_values: In "CONSTANT" mode, the scalar pad value to use. Must be
          same type as `tensor`.

      Returns:
        A `Tensor`. Has the same type as `tensor`.
    """

    if mode.upper() == 'CYCLIC':
        with tf.name_scope(name):
            rank = paddings.shape.as_list()[0]
            perm = [(i + 1) % rank for i in range(rank)]

            out = tensor
            for r in range(rank):
                # Create the padding slices and concat them to the original tensor
                out = tf.concat(
                    [out[tf.shape(out)[0] - paddings[r, 0]:, ...], out, out[:paddings[r, 1], ...]],
                    axis=0
                )

                # Move dimension of interest to position 0 for next step
                out = tf.transpose(out, perm)
    else:
        out = tf.pad(
            tensor,
            paddings,
            mode=mode,
            constant_values=constant_values,
            name=name
        )

    return out


def cyclic_padding(tensor: tf.Tensor, kernel_size: tuple, strides: tuple, scope: str = None):
    """
    This operation is a high-level wrapper for tf.pad(mode="CYCLIC") that computes the amount of
    padding for each dimension based on the `kernel_size` and `strides` specified. This function
    is intended to be a convenience wrapper when using convolutional layers with cyclic padding.
    It takes a tf.Tensor(shape=[N, H, W, C]) and performs zero padding in H and cyclic padding in W.

    For example:
    ```python
    t = tf.random.normal([4, 10, 50, 2])

    k_size = (3, 3)
    strides = (1, 1)

    t_padded = tf_helpers.cyclic_padding(t, k_size, strides)
    tf.layers.conv2d(t_padded, k_size, strides, padding='valid')

    # results in the same shape as
    # tf.layers.conv2d(t, k_size, strides, padding='same')
    ```

    Parameters:
        tensor: A `Tensor` of rank 4.
        kernel_size: A `tuple` of two integers.
        strides: A `tuple` of two integers.
        scope (str): A name for the operation.

    Returns:
        A `Tensor`. Has same type as `tensor`.
    """

    with tf.variable_scope(name_or_scope=scope, default_name='cyclic_padding'):

        inp_h, inp_w = tensor.get_shape().as_list()[1:3]

        pad_top, pad_bottom, pad_left, pad_right = get_padding_sizes(
            (inp_h, inp_w), kernel_size, strides)

        # Zero padding in the vertical dimension
        inp_pad_vertical = tf.pad(tensor, [[0, 0], [pad_top, pad_bottom], [0, 0], [0, 0]],
                                  mode='CONSTANT', constant_values=0)

        # Cyclic padding in the horizontal dimension
        out = pad(inp_pad_vertical,
                  tf.convert_to_tensor([[0, 0], [0, 0], [pad_left, pad_right], [0, 0]]),
                  mode='CYCLIC')
    return out
