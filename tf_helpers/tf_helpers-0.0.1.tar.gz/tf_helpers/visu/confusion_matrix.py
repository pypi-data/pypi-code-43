# -*- coding: utf-8 -*-

__author__ = """Larissa Triess"""
__email__ = 'mail@triess.eu'

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from mpl_toolkits import axes_grid1


def confusion_matrix_image(
        tf_conf_mat: tf.Tensor, class_names: list, fig_dpi: int = 320, fig_size: int = 3,
        normalize: bool = True, cmap: plt.cm = plt.cm.Blues, scope: str = None
):

    """
    Visualization of the confusion matrix as an image to publish in TensorBoard with tf.summary.image

    Parameters:
        tf_conf_mat (tf.Tensor): A confusion matrix defined as
            Tensor(shape=[len(class_names), len(class_names)], dtype=tf.float32).
        class_names (list): The names of the classes (str).
        fig_dpi (int): The resolution of the output image.
        fig_size (int): The size of the figure.
        normalize (bool): If `True` numbers shown in the image will to normalized to 100%,
            otherwise absolute numbers will be depicted. Default is `True`.
        cmap (matplotlib.pyplot.cm): A `matplotlib` color map with which to paint the image.
            Default to `matplotlib.pyplot.cm.Blues`.
        scope (str): The name scope of the function. Defaults to `confusion_matrix_image`.

    Returns:
        Tensor(shape=[1, fig_dpi * fig_size, fig_dpi * fig_size, 3], dtype=tf.uint8): An RGB image.
            The first dimension corresponds to the `batch_size` to be published with `tf.summary.image`.

    Raises:
        ValueError: If length of class_names does not match the dimensions of tf_conf_mat.
    """

    if not tf_conf_mat.shape == [len(class_names)]*2:
        raise ValueError('Shape missmatch between `class_names` and `tf_conf_mat`. '
                         'The number of elements in `class_names` must be equal to the shape of '
                         'each dimension of `tf_conf_mat`.')

    with tf.name_scope(name=scope, default_name='confusion_matrix_image'):

        def add_colorbar(im, aspect=20, pad_fraction=2.0):
            divider = axes_grid1.make_axes_locatable(im.axes)
            width = axes_grid1.axes_size.AxesY(im.axes, aspect=0.6 / aspect)
            pad = axes_grid1.axes_size.Fraction(pad_fraction, width)
            current_ax = plt.gca()
            cax = divider.append_axes("right", size=width, pad=pad)
            plt.sca(current_ax)
            return im.axes.figure.colorbar(im, cax=cax)

        def process_matrix(conf_mat):
            conf_mat = conf_mat.numpy()  # eager tensor to numpy array
            # normalize the confusion matrix (numbers will be displayed in percent)
            if normalize:
                _conf_mat = conf_mat
                conf_mat_sum = _conf_mat.sum(axis=1)
                _conf_mat[conf_mat_sum > 0] /= conf_mat_sum[conf_mat_sum > 0, None]
                conf_mat = _conf_mat * 100
                int_rest = conf_mat - conf_mat.astype(np.int32)
                sum_rest = np.round(int_rest.sum(axis=1)).astype(np.int32)
                rest_ordering = np.argsort(np.argsort(int_rest, axis=1), axis=1)
                rest_rounding = (
                    rest_ordering >= rest_ordering.shape[0] - sum_rest[:, None]
                )
                conf_mat = conf_mat.astype(np.int32) + rest_rounding.astype(np.int32)
                vminmax = dict(vmin=0, vmax=100)
            else:
                conf_mat = conf_mat.astype(np.float32)
                vminmax = dict()

            # plot confusion matrix to be displayed on TensorBoard
            np.set_printoptions(precision=2)  # limit display of floats to 2 decimals

            fig = Figure(figsize=(fig_size, fig_size), dpi=fig_dpi, facecolor='w', edgecolor='k')
            ax = fig.add_subplot(1, 1, 1)
            im = ax.imshow(conf_mat, interpolation='nearest', cmap=cmap, **vminmax)
            add_colorbar(im).ax.tick_params(labelsize=fig_size)

            ax.set_xlabel('Predicted Label', fontsize=fig_size)
            ax.set_xticks(np.arange(conf_mat.shape[1]))
            ax.set_xticklabels(class_names, fontsize=fig_size / 2 + 1, ha='right',
                               rotation=45, rotation_mode='anchor')
            ax.xaxis.set_label_position('top')
            ax.xaxis.tick_bottom()

            ax.set_ylabel('True Label', fontsize=fig_size)
            ax.set_yticks(np.arange(conf_mat.shape[0]))
            ax.set_ylim(conf_mat.shape[0] - 0.5, -0.5)
            ax.set_yticklabels(class_names, fontsize=fig_size / 2 + 1, va='center')
            ax.yaxis.set_label_position('right')
            ax.yaxis.tick_left()

            thresh = 2 * (conf_mat.max() / 3.0)
            for i in range(conf_mat.shape[0]):
                for j in range(conf_mat.shape[1]):
                    number_format = '{0:.1f}' if conf_mat.dtype == np.float32 else '{}'
                    ax.text(
                        j,
                        i,
                        number_format.format(conf_mat[i, j])
                        if conf_mat[i, j] != 0
                        else ".",
                        horizontalalignment="center",
                        fontsize=3 * fig_size / 4,
                        verticalalignment="center",
                        color="white" if conf_mat[i, j] > thresh else "black",
                    )

            canvas = FigureCanvasAgg(fig)
            canvas.draw()  # draw the canvas, cache the renderer
            image = np.fromstring(canvas.tostring_rgb(), dtype=np.uint8)
            image = image.reshape((fig_dpi * fig_size, fig_dpi * fig_size, 3))

            fig.clear()
            plt.close(fig)

            return image

        tf_image = tf.py_function(func=process_matrix,
                                  inp=[tf_conf_mat],
                                  Tout=tf.uint8,
                                  name='process_matrix')

        tf_image = tf.expand_dims(tf_image, 0)
        tf_image.set_shape([1, fig_dpi * fig_size, fig_dpi * fig_size, 3])

    return tf_image
