# -*- coding: utf-8 -*-

__author__ = """Larissa Triess"""
__email__ = 'mail@triess.eu'

import tensorflow as tf
from matplotlib.pylab import get_cmap


def expand_image_height(
        tf_image: tf.Tensor, factor: int, scope: str = None
):

    """
    Enlarges the input image-like tensor [H, W, C] of rank 3 in the first dimension (H)

    Parameters:
        tf_image (tf.Tensor): A rank 3 `Tensor` of shape [H, W, C].
        factor (int): The factor specifies how many multiples of each element in H are produced.
        scope (str): The name scope of the function.

    Returns:
        Tensor(shape=[H * factor, W, C], dtype=tf.image.dtype)

    Raises:
        NotImplementedError: When `tf_image` has rank 4. Batch dimension is not yet supported.
        ValueError: When `tf_image` has a different rank than 3 and 4.
        ValueError: If `factor` is not an integer greater or equal to 1.

    """

    shape = tf_image.shape

    if len(shape) == 4:
        raise NotImplementedError('Expand image height function does not support batched tensors.')
    if not len(shape) == 3:
        raise ValueError('The input tensor must be of rank 3.')
    if not isinstance(factor, int) or factor < 1:
        raise ValueError('Expected integer greater or equal to 1. I got {}.'.format(factor))

    with tf.name_scope(name=scope, default_name='expand_height'):
        shape = [shape[0] * factor, shape[1], shape[2]]
        tf_image = tf.expand_dims(tf_image, axis=1)
        tf_image = tf.tile(tf_image, multiples=[1, factor, 1, 1])
        tf_image = tf.reshape(tf_image, shape)
    return tf_image


def create_image(
        tensor: tf.Tensor, minval: float = 0.0, maxval: float = None,
        cmap: str = 'viridis', cycle_color_map: int = 1,
        mask: tf.Tensor = None, exclude_color: tuple = (0, 0, 0),
        expand_height: int = 1, scope: str = None,
):

    """
    Visualization of a two-dimensional tf.Tensor as a color image.

    Parameters:
        tensor (tf.Tensor): An image-like Tensor(shape=[H, W], dtype=tf.float32).
        minval (float): The minimum value for clipping. Defaults to 0.0.
        maxval (float): The maximum value for clipping.
        cmap (str): A valid name for a matplotlib color map or `gray`.
        cycle_color_map (int): Repeats the colormap the defined number of times in a
            continuous permutation pattern. Useful if high ranges within `tensor` shall
            be visualized in high color resolution. Defaults to 1.
        mask (tf.Tensor): A boolean mask with the same shape as `tensor` that indicates
            which indices shall be excluded from the color mapping.
            Tensor(shape=[H, W], dtype=tf.bool).
        exclude_color (tuple): An (R, G, B) color in range [0, 255] that defines the
            color of the indices that are excluded by `mask`. Defaults to black (0, 0, 0).
        expand_height (int): A factor that specifies how many multiples of each element
            in H are produced. Useful if H << W. Default to 1.
        scope (str): The name scope of the function.

    Returns:
        Tensor(shape=[1, H * expand_height, W, 3], dtype=tf.uint8): An RGB image.
            The first dimension corresponds to the `batch_size` to be published with `tf.summary.image`.

    Raises:
        ValueError: When shape of `tensor` and `mask` are not equal if `mask` is not None.
        ValueError: When type of `mask` is not tf.bool if `mask` is not None.
        ValueError: If `maxval` is lower or equal to `minval`.

    TODO:
        * add support for batched tensors
        * add support for expand_width
    """

    if mask is not None:
        if not tensor.shape == mask.shape:
            raise ValueError('`tensor` and `mask` must have same shape. {} vs. {}'.format(
                tensor.shape, mask.shape))
        if not mask.dtype == tf.bool:
            raise TypeError('`mask` must have type `tf.bool` but is {}'.format(mask.dtype))

    if maxval is not None and maxval <= minval:
        raise ValueError('Clipping values should be defined as `minval` < `maxval`. '
                         'Got {} !< {}.'.format(minval, maxval))

    if not isinstance(cycle_color_map, int) or cycle_color_map < 1:
        raise ValueError('`cycle_color_map` must be an integer greater than 1.')

    with tf.name_scope(name=scope, default_name='create_image'):

        # normalization
        maxval = maxval if maxval is not None else tf.reduce_max(tensor)
        tensor = tf.clip_by_value(tensor, minval, maxval)
        tensor = tf.round((tensor - minval) * 255 * cycle_color_map) / (maxval - minval)
        indices = tf.cast(tensor, dtype=tf.int32)

        # colorization
        if cmap == 'gray':
            colors = tf.range(start=0, limit=256, delta=1, dtype=tf.uint8)
            tf_image = tf.stack([tf.gather(colors, indices), ] * 3, axis=-1)
        else:
            cmap_colors = get_cmap(cmap).colors
            cm = [cmap_colors if i % 2 else cmap_colors[::-1] for i in range(cycle_color_map)]
            colors = tf.cast(tf.concat(cm, axis=0) * 255, dtype=tf.uint8)
            tf_image = tf.gather(colors, indices)

        if mask is not None:
            stacked_mask = tf.stack([mask] * 3, axis=-1)
            tf_image = tf.where(stacked_mask,
                                tf_image,
                                exclude_color * tf.ones_like(stacked_mask, dtype=tf.uint8))

        # expand the image height for better visualization in TensorBoard
        tf_image = expand_image_height(tf_image, expand_height)
        tf_image = tf_image[tf.newaxis, :, :, :]

    return tf_image
