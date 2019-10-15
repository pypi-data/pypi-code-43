# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/


__authors__ = ["J. Garriga"]
__license__ = "MIT"
__date__ = "10/09/2019"


import numpy
import cv2
from scipy.ndimage import center_of_mass, fourier_shift
from skimage import feature
from enum import Enum

from darfix.io import utils
from.autofocus import normalized_variance


class ShiftApproaches(Enum):
    """
    Different shifts approaches that can be used for the shift detection and correction.
    """
    LINEAR = "linear"
    FFT = "fft"

    @staticmethod
    def list():
        return list(map(lambda c: c.value, ShiftApproaches))


def compute_com(data):
    """
    Compute the center of mass of a stack of images.
    First it computes the intensity of every image (by summing its values), and then
    it uses scipy ``center_of_mass`` function to find the centroid.

    :param numpy.ndarray data: stack of images.
    :returns: the vector of intensities and the com.
    """
    intensity = data.sum(axis=1).sum(axis=1)
    return intensity, int(center_of_mass(intensity)[0])


def diff_com(img1, img2):
    """
    Finds the difference between the center of mass of two images.
    This can be used to find the shift between two images with distinguished
    center of mass.
    """
    return numpy.array(center_of_mass(img2)) - numpy.array(center_of_mass(img1))


def find_shift(img1, img2, upsampling_factor=1):
    """
    Uses the function ``register_translation`` from skimage to find the shift between two images.

    :param array_like img1: first image.
    :param array_like img2: second image, must be same dimensionsionality as ``img1``.
    :param int upsampling_factor: optional.
    """
    return feature.register_translation(img1, img2, upsampling_factor, return_error=False)


def _numpy_fft_shift(img, dx, dy):
    """
    Shift an image by Fourier approach using Numpy library.

    :param array_like img: Image to shift
    :param number dx: shift in x axis
    :param number dy: shift in y axis
    :returns: ndarray
    """
    img = numpy.asarray(img, dtype=numpy.float32)
    xnum, ynum = img.shape
    """
    Create grid to apply the Fourier transformed theory for translated images.
    Each value of each matrix (Nx, Ny) correspons to the coordinate of the corresponding pixel.
    """
    Nx, Ny = numpy.meshgrid(numpy.fft.fftfreq(ynum), numpy.fft.fftfreq(xnum))
    c = numpy.fft.fft2(img) * numpy.exp(-2 * numpy.pi * 1j * (dx * Nx + dy * Ny))
    return numpy.fft.ifft2(c).real


def _opencv_fft_shift(img, dx, dy):
    """
    Shift an image by Fourier approach using opencv library.

    :param array_like img: Image to shift
    :param number dx: shift in x axis
    :param number dy: shift in y axis
    :returns: ndarray
    """
    img = numpy.asarray(img, dtype=numpy.float32)
    ynum, xnum = img.shape
    """
    Create grid to apply the Fourier transformed theory for translated images.
    Each value of each matrix (Nx, Ny) corresponds to the coordinate of the corresponding pixel
    divided by the size of the image.
    """
    Nx, Ny = numpy.meshgrid(numpy.fft.fftfreq(xnum), numpy.fft.fftfreq(ynum))
    dft = cv2.dft(img, flags=cv2.DFT_COMPLEX_OUTPUT)
    dft = dft[..., 0] + 1j * dft[..., 1]
    dft = dft * numpy.exp(-2 * numpy.pi * 1j * (dx * Nx + dy * Ny))
    real = numpy.reshape(dft.real, dft.real.shape + (1,))
    imag = numpy.reshape(dft.imag, dft.imag.shape + (1,))
    dft = numpy.concatenate((real, imag), axis=2)
    return cv2.idft(dft, flags=cv2.DFT_SCALE + cv2.DFT_REAL_OUTPUT)


def _scipy_fft_shift(img, dx, dy):
    """
    Shift an image by Fourier approach using scipy library.

    :param array_like img: Image to shift
    :param number dx: shift in x axis
    :param number dy: shift in y axis
    :returns: ndarray
    """
    return numpy.fft.ifftn(fourier_shift(numpy.fft.fftn(img), [dy, dx])).real


def apply_shift(img, shift, shift_approach='fft'):
    """
    Function to apply the shift to an image.

    :param 2-dimensional array_like img: Input array, can be complex.
    :param 2-dimensional array_like shift: The shift to be applied to the image. ``shift[0]``
        refers to the y-axis, ``shift[1]`` refers to the x-axis.
    :param Union[`linear`, `fft`] shift_approach: The shift method to be used to apply the shift.
    :returns: real ndarray
    """
    assert shift_approach in ShiftApproaches.list(), utils.assert_string("Attribute shift_approach",
                                                                         ShiftApproaches.list())
    if shift_approach == ShiftApproaches.LINEAR.value:
        img = img.astype(numpy.int16)
        M = numpy.float32([[1, 0, shift[1]], [0, 1, shift[0]]])
        return cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))
    else:
        return _opencv_fft_shift(img, shift[1], shift[0])


def normalize(x):
    """
    Normalizes a vector or matrix.
    """
    if not numpy.count_nonzero(x):
        return x
    return x / numpy.linalg.norm(x)


def improve_linear_shift(data, v, h_max, h_step, nimages=None, shift_approach='linear'):
    """
    Function to find the best shift between the images. It loops ``h_max * h_step`` times,
    applying a different shift each, and trying to find the one that has the best result.

    :param array_like data: The stack of images.
    :param 2-dimensional array_like v: The vector with the direction of the shift.
    :param number h_max: The maximum value that h can achieve, being h the shift between
        images divided by the vector v (i.e the coordinates of the shift in base v).
    :param number h_step: Spacing between the ``h`` tried. For any `` shift = h * v * idx``,
        where ``idx`` is the index of the image to apply the shift to, this is the distance
        between two adjacent values of h.
    :param int nimages: The number of images to be used to find the best shift. It has to
        be smaller or equal as the length of the data. If it is smaller, the images used
        are chosen using `numpy.random.choice`, without replacement.
    :param Union[`linear`,`fft`] shift_approach: The shift method to be used to apply the shift.
    :returns: ndarray
    """
    v = numpy.asanyarray(v)
    iData = range(data.shape[0])

    if nimages:
        iData = numpy.random.choice(iData, nimages, False)

    score = {}
    utils.advancement_display(0, h_max, "Finding shift")
    for h in numpy.arange(0, h_max, h_step):
        result = numpy.zeros(data[0].shape)
        for iFrame in iData:
            shift = h * v * iFrame
            result += apply_shift(data[iFrame], shift, shift_approach)

        # Compute score using normalized variance
        # TODO: add more autofocus options
        score[h] = normalized_variance(result)
        utils.advancement_display(h + h_step, h_max, "Finding shift")

    optimal_h = max(score.keys(), key=(lambda k: score[k]))
    return optimal_h


def shift_detection(data, h_max=0.5, h_step=0.01):
    """
    Finds the linear shift from a set of images.

    :param ndarray data: Array with the images.
    :returns: A vector of length the number of images with the linear shift
        to apply to every image.
    :rtype: ndarray
    """
    intensity, com = compute_com(data)
    first_sum = numpy.sum(data[:com], axis=0)
    second_sum = numpy.sum(data[com:], axis=0)
    shift = find_shift(first_sum, second_sum, 1000)
    v = normalize(shift)
    h = improve_linear_shift(data, v, h_max, h_step)
    return numpy.outer(h * v, numpy.arange(data.shape[0]))


def shift_correction(data, n_shift, shift_approach='fft', callback=None):
    """
    Function to apply shift correction technique to stack of images.

    :param array_like data: The stack of images to apply the shift to.
    :param array_like n_shift: Array with the shift to be applied at every image.
        The first row has the shifts in the y-axis and the second row the shifts
        in the x-axis. For image ``i`` the shift applied will be:
        ``shift_y = n_shift[0][i] shift_x = n_shift[1][i]```.
    :param Union[`linear`,`fft`] shift_approach: Name of the shift approach
        to be used. Default: `fft`.
    :param Union[None,Function] callback: Callback function to update the
        progress.
    :returns: The shifted images.
    :rtype: ndarray
    """

    shift = numpy.asanyarray(n_shift)

    if not numpy.any(shift):
        return data

    assert shift.shape == (2, len(data)), "n_shift list has to be of same size as stack of images"

    shifted_data = numpy.empty(data.shape, dtype=numpy.float32)

    utils.advancement_display(0, len(data), "Applying shift")

    for count, frame in enumerate(data):
        shifted_data[count] = apply_shift(frame, shift[:, count], shift_approach)
        utils.advancement_display(count + 1, len(data), "Applying shift")
        if callback:
            callback(int(count / len(data) * 100))

    if data.dtype.kind == 'f':
        if data.dtype.itemsize > shifted_data.dtype.itemsize:
            import warnings
            warnings.warn("Precision loss to float32")
    else:
        import warnings
        warnings.warn("Data cast to float32")

    return shifted_data


def random_search(data, optimal_shift, iterations, sigma=None, shift_approach='linear'):
    """
    Function that performs random search to a set of images to find an improved vector of shifts (one
    for each image). For this, it adds to the optimal shift a series of random samples obtained from
    a multivariate normal distribution, and selects the one with best score.

    :param array_like data: Set of images.
    :param ndarray optimal_shift: Array with two vectors with the linear shift found for axis y and x.
    :param int iterations: Number of times the random search should be done.
    :param number sigma: Standard deviation of the distribution.
    :param Union[`linear`,`fft`] shift_approach: Name of the shift approach
        to be used. Default: `linear`.
    :returns: A vector of length the number of images with the best shift found for every image.
    :rtype: ndarray
    """
    best_score = -numpy.inf
    best_result = numpy.empty(optimal_shift.shape)

    if sigma is None:
        # Using shift from second image
        sigma = abs(optimal_shift[:, 1] / 3)

    utils.advancement_display(0, iterations)
    for i in range(iterations):
        result = numpy.zeros(data[0].shape)
        normal = numpy.random.multivariate_normal((0, 0), sigma * numpy.eye(2), len(data)).T
        n_shift = optimal_shift + normal
        for iFrame in range(len(data)):
            shifty = n_shift[0][iFrame]
            shiftx = n_shift[1][iFrame]
            result += apply_shift(data[iFrame], [shifty, shiftx], shift_approach)
        score = normalized_variance(result)
        if best_score < score:
            best_result = n_shift
            best_score = score

        utils.advancement_display(i + 1, iterations)

    return best_result
