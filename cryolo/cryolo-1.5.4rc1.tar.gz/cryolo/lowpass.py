#
# COPYRIGHT
#
# All contributions by Thorsten Wagner:
# Copyright (c) 2017 - 2019, Thorsten Wagner.
# All rights reserved.
#
# ---------------------------------------------------------------------------
#         Do not reproduce or redistribute, in whole or in part.
#      Use of this code is permitted only under licence from Max Planck Society.
#            Contact us at thorsten.wagner@mpi-dortmund.mpg.de
# ---------------------------------------------------------------------------
#
import multiprocessing
import os
import warnings

import numpy as np
import scipy.fftpack as fft

import cryolo.imagereader as imagereader

LOCK = None


def window(image, width):
    """

    :param image:
    :param width: Width of the gaussian filter in fourier pixel
    :return:
    """
    center_image_y = image.shape[0] / 2
    center_image_x = image.shape[1] / 2
    x_coord_vec = np.linspace(0, image.shape[1], image.shape[1])
    y_coord_vec = np.linspace(0, image.shape[0], image.shape[0])
    x_coord_mat, y_coord_mat = np.meshgrid(x_coord_vec, y_coord_vec, sparse=True)
    dist_mat = np.float16(
        np.sqrt(
            ((y_coord_mat - center_image_y) ** 2)
            + ((x_coord_mat - center_image_x) ** 2)
        )
        + width / 2
    )
    gmask = np.sin(np.pi * dist_mat / (width - 1))
    gmask[dist_mat > width] = 0

    return image * gmask


def next_power_of2(number):
    return int(np.power(2, np.ceil(np.log2(number))))


def zero_pad(img, size_new):
    pad_extends = []
    dif_shape_y = size_new[0] - img.shape[0]
    dif_shape_x = size_new[1] - img.shape[1]

    pad_extends.append((dif_shape_y // 2, dif_shape_y // 2 + dif_shape_y % 2))
    pad_extends.append((dif_shape_x // 2, dif_shape_x // 2 + dif_shape_x % 2))

    padded = np.pad(img, pad_extends, "symmetric")

    return padded, pad_extends


def low_pass_filter(img, filter_width):
    """
    Low pass filter
    :param img: Image to be filtered (numpy array)
    :param filter_width: Width of the gaussian filter in fourier pixel
    :return: Return low pass filtered image
    """
    input_image_shape = img.shape
    # Zero Pad
    next_shape_y = next_power_of2(img.shape[0])
    next_shape_x = next_power_of2(img.shape[1])
    new_image_size = (next_shape_y, next_shape_x)
    padded, pad_extends = zero_pad(img, new_image_size)

    # The input image is not needed anymore at this point
    del img

    # FFT
    img_fft = fft.fft2(padded)

    # Padded image is not needed anymore
    del padded

    img_fft = fft.fftshift(img_fft)
    # Windowing with cosine window
    img_fft_windowed = window(img_fft, filter_width)
    del img_fft

    # Backward fft
    img_fft_windowed = fft.ifftshift(img_fft_windowed)
    img_filtered = fft.ifft2(img_fft_windowed)

    del img_fft_windowed
    # Crop
    img_cropped = img_filtered[
        pad_extends[0][0] : (pad_extends[0][0] + input_image_shape[0]),
        pad_extends[1][0] : (pad_extends[1][0] + input_image_shape[1]),
    ]

    del img_filtered

    return np.real(img_cropped)


def filter_images(images, filter_cutoff, filter_tmp_path, num_cpu=-1, resize_to=None):
    """
    Function will filter images gives in the image dictonary, write them into the filter_output_path

    :param images: list of images
    :param filter_cutoff: Absolute cutoff frequence (0-0.5)
    :param filter_tmp_path: Output directory for temporary files
    :return: None
    """

    if not os.path.isdir(filter_tmp_path):
        os.makedirs(filter_tmp_path)

    # Correct absolute filenames
    adapted_paths = [
        img["filename"][1:] if img["filename"][0] == "/" else img["filename"]
        for img in images
    ]

    # Create file paths for filtered files
    filtered_file_paths = [
        os.path.join(filter_tmp_path, img_pth) for img_pth in adapted_paths
    ]

    # Check if files are already existing
    already_filtered = [os.path.exists(file) for file in filtered_file_paths]

    # Get index of images that are already filtered
    index_images_already_filtered = [i for i, x in enumerate(already_filtered) if x]

    # Updates paths for already filtered images
    for index in index_images_already_filtered:
        images[index]["filename"] = filtered_file_paths[index]

    # Get index of images that have to be filtered
    index_images_to_filter = [
        i
        for i, x in enumerate(already_filtered)
        if not x and os.path.basename(filtered_file_paths[i])[0] != "."
    ]

    # Create argument tubles for them
    arg_tubles = []
    arg_tubles.extend(
        [
            (images[i]["filename"], filter_cutoff, filter_tmp_path, -1, -1, resize_to)
            for i, is_filtered in enumerate(already_filtered)
            if not is_filtered
        ]
    )

    # Do the filtering
    num_processes = None
    if num_cpu > 0:
        num_processes = num_cpu
    lock = multiprocessing.Lock()
    pool = multiprocessing.Pool(
        initializer=init, initargs=(lock,), maxtasksperchild=1, processes=num_processes
    )
    all_filtered_images_paths = pool.starmap(
        filter_single_image_and_write_to_disk, arg_tubles, chunksize=1
    )
    pool.close()
    pool.join()

    # Update paths of newly filtered images
    for i, index in enumerate(index_images_to_filter):
        images[index]["filename"] = all_filtered_images_paths[i]


def filter_single_image_and_write_to_disk(
    img_path,
    filter_cutoff,
    output_path_filtered_images,
    img_num=-1,
    total_num=-1,
    resize=None,
):
    """
    Filteres the image in img_path, save it to disk and returns the path to the filtered images
    :param img_path: Path to image to filter
    :param filter_cutoff: Absolute frequence (0 - 0.5)
    :param output_path_filtered_images: Output path for filtered images
    :param resize: tuple with image size. the image will be downsized to this size before filtering
    :return: Path to the filtered image
    """
    dirname = os.path.dirname(img_path)
    if dirname.startswith("/"):
        dirname = dirname[1:]
    filtered_image_folder = os.path.join(output_path_filtered_images, dirname)
    filtered_img_tmp_file_path = os.path.join(
        filtered_image_folder, os.path.basename(img_path)
    )
    if not os.path.exists(filtered_img_tmp_file_path):
        global LOCK
        if filter_cutoff > 0.5:
            warnings.simplefilter("once", UserWarning)
            print("Filter cutoff has to be smaller than 0.5. Set it to 0.5")
            filter_cutoff = 0.5

        if LOCK is not None:
            with LOCK:
                if not os.path.isdir(filtered_image_folder):
                    os.makedirs(filtered_image_folder)
        else:
            try:
                if not os.path.isdir(filtered_image_folder):
                    os.makedirs(filtered_image_folder)
            except FileExistsError:
                pass

        if img_num != -1 and total_num != -1:
            print(
                "Filtering ",
                img_path,
                "( Progress:",
                int(img_num / total_num * 100),
                "% )",
            )
        else:
            print("Filtering ", img_path)

        image_filtered = filter_single_image(
            img_path=img_path, filter_cutoff=filter_cutoff, resize_to=resize
        )
        imagereader.image_write(filtered_img_tmp_file_path, image_filtered)
        del image_filtered
    return filtered_img_tmp_file_path


def filter_single_image(img_path, filter_cutoff, resize_to=None):
    image = imagereader.image_read(img_path)
    cutoff_factor = 1.0
    if resize_to is not None:
        cutoff_factor = image.shape[0] / resize_to[0]
        from PIL import Image

        image = np.array(
            Image.fromarray(image).resize(resize_to, resample=Image.BILINEAR)
        )
    image_filtered = low_pass_filter(
        image, 2 * image.shape[1] * filter_cutoff * cutoff_factor
    )
    del image
    return image_filtered


def init(lock):
    """
    Init for multiprocessing
    :param lock: Lock object
    :return: None
    """
    global LOCK
    LOCK = lock
