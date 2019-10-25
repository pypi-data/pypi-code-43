#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 01:16:40 2018

@author: henrik
"""
import numpy as np
import scipy
from skimage.measure import regionprops
from scipy.spatial import cKDTree
from mahotas.labeled import filter_labeled, border
from mahotas.labeled import relabel as mrelabel
from mahotas.labeled import labeled_max
from .steepest import _compute_neighbours, _validate_connectivity
from .misc import merge  # , crop

# TODO: Add connectivity parameter
# TODO: Implement opening
# TODO: Implement closing
# TODO: Add iterations parameter to all


def erode(A):
    """ Erode labels. """
    B = A.copy()
    B[B * (np.abs(scipy.ndimage.laplace(B)) > 0) > 0] = 0
    return B


def dilate(lab_img, size=1):
    """ Dilate labels. """
    # TODO: Should really be a mode filter, no?
    B = scipy.ndimage.maximum_filter(lab_img, size)
    B[lab_img != 0] = lab_img[lab_img != 0]
    return B


def remove_labels_size(lab_img, resolution=None, min_size=None, max_size=None):
    """ Remove labels based on size. Background assumed 0. """
    rp = regionprops(lab_img)
    sizes = np.array([len(rr.coords) for rr in rp], dtype='float')
    mask = np.zeros(len(rp), dtype='bool')

    if resolution is not None:
        sizes *= np.product(resolution)
    if min_size is not None:
        mask[sizes < min_size] = True
    if max_size is not None:
        mask[sizes > max_size] = True

    labels = np.array([rr.label for rr in rp])
    labels = labels[mask]
    lab_img[np.isin(lab_img, labels)] = 0

    return lab_img


#    return filter_labeled(lab_img, remove_bordering, min_size, max_size)[0]

def relabel(lab_img):
    """ Remove labels. Background assumed 0. """
    return mrelabel(lab_img, inplace=False)[0]


def merge_labels_distance(lab_img, threshold, resolution=None, bg=0, mode='center', int_img=None):
    """ Merge labeled objects based on the distance between the attractors.

    An attractor is defined as the voxel with the highest intensity in each label.
    It can therefore be advisable to use the smoothened image as the input intensity
    image.

    Parameters
    ----------
    lab_img : ndarray
        Labeled image.
    int_img : ndarray
        Intensity image. Same shape as lab_img.
    threshold : float
        Euclidean distance used to determine label merging.
    resolution : ndarray of length lab_img.ndim
        Spatial resolution of the images.
    bg : int
        Background label.

    Returns
    -------
    lab_img : ndarray
        The modified, labeled image.
    """
    rp = regionprops(lab_img, int_img)
    if mode in ['max', 'maximum'] and int_img is not None:
        boas = np.array([rr.coords[np.argmax(
            int_img[rr.coords[:, 0], rr.coords[:, 1], rr.coords[:, 2]])] for rr in rp])
    elif mode in ['min', 'minimum'] and int_img is not None:
        boas = np.array([rr.coords[np.argmin(
            int_img[rr.coords[:, 0], rr.coords[:, 1], rr.coords[:, 2]])] for rr in rp])
    elif mode in ['center', 'com', 'center of mass', 'center_of_mass']:
        boas = np.array([rr.coords[np.argmin(
            np.sum((rr.coords - np.mean(rr.coords, axis=0))**2, axis=1))] for rr in rp])
    else:
        raise ValueError('TODO')
    labels = np.array([rr.label for rr in rp])
    del rp

    if resolution is None:
        resolution = np.ones((lab_img.ndim, ))
    boas = np.multiply(boas, resolution)

    # get clusters from distances
    tree = cKDTree(boas)
    clusters = np.array(tree.query_ball_tree(tree, threshold))
#    clusters = np.unique(clusters)
    clusters = merge(clusters)
    clusters = np.array([np.array(list(x)) for x in clusters])
    clusters = np.array([labels[cc] for cc in clusters])
    del tree

    # label
    lab_img_raveled = lab_img.ravel()
    for ii, labels in enumerate(clusters):
        lab_img_raveled[np.in1d(lab_img_raveled, labels)] = np.min(labels)

    return lab_img


def merge_labels_small2closest(lab_img, threshold, resolution=None, distance_upper_bound=np.inf):
    """ Merge labeled objects under a given size with the closest large attractor.

    An attractor is defined as the voxel with the highest intensity in each label.
    It can therefore be advisable to use the smoothened image as the input intensity
    image.

    Parameters
    ----------
    lab_img : ndarray
        Labeled image.
    threshold : float
        Threshold size to determine merging.
    resolution : ndarray of length lab_img.ndim
        Spatial resolution of the images.
    distance_upper_bound : float
        Maximal distance for when to merge attractors.

    Returns
    -------
    lab_img : ndarray
        The modified, labeled image.
    """
    if resolution is None:
        resolution = np.ones((lab_img.ndim, ))

    # categorise
    import sys

    to_merge = filter_labeled(lab_img, max_size=threshold)[0].astype('bool')
    targets = filter_labeled(
        lab_img, min_size=threshold + sys.float_info.epsilon)[0].astype('bool')

    # get coordinates
    inds = np.indices(lab_img.shape)
    inds = np.reshape(inds, (lab_img.ndim, -1)).T
    to_merge = inds[to_merge.ravel()]
    targets = inds[targets.ravel()]

    # find closest pairs
    tree = cKDTree(np.multiply(targets, resolution))
    dists, neighbour = tree.query(np.multiply(to_merge, resolution))
    to_process = dists < distance_upper_bound
    target_coords = targets[neighbour[to_process]]
    to_merge_coords = to_merge[to_process]

    # merge
    lab_img[to_merge_coords[:, 0],
            to_merge_coords[:, 1],
            to_merge_coords[:, 2]] = lab_img[target_coords[:, 0],
                                             target_coords[:, 1],
                                             target_coords[:, 2]]

    return lab_img


def remove_labels_intensity(lab_img, int_img, threshold, bg=0):
    """ Remove labels based on their (mean) intensity. """
    # TODO add method for choosing between min / max / mean
    rp = regionprops(lab_img, int_img)
    lab_img_raveled = lab_img.ravel()

    to_remove = np.array(
        [rr.label for rr in rp if rr.mean_intensity < threshold])

    lab_img_raveled[np.in1d(lab_img_raveled, to_remove)] = bg
    return lab_img


def merge_labels_depth(lab_img, int_img, threshold, connectivity=None, offset=None):
    """ Merge neighbouring labels by comparing the peak intensities with the minimal
    border intensity, in order to get an estimate of the domain depths relative
    to each other. """

    connectivity, offset = _validate_connectivity(
        lab_img.ndim, connectivity, offset)

    # pad
    pad_width = [(p, p) for p in offset]
    lab_img = np.pad(lab_img, pad_width, mode='constant')
    int_img = np.pad(int_img, pad_width, mode='constant')

    flat_neighbourhood = _compute_neighbours(lab_img, connectivity, offset)

    lab_img_raveled = lab_img.ravel()

    while True:
        labels = np.unique(lab_img_raveled)[1:]

        # get what domains are neighbouring each domain
        neighbouring_domains = []
        for label in labels:
            indices = np.where(lab_img_raveled == label)[0]
            point_neighbours = np.array(
                list(map(lambda x: x + flat_neighbourhood, indices)))
            point_neighbours_labels = lab_img_raveled[point_neighbours]
            neighbouring_labels = np.unique(
                point_neighbours_labels[point_neighbours_labels > 0])
            neighbouring_domains.append(neighbouring_labels)

        # check basin depths
        labels_maxima = labeled_max(int_img, lab_img)[1:]
        to_merge = []
        borders = np.zeros(lab_img.shape, dtype=np.bool)
        for label1, neighbours in enumerate(neighbouring_domains, start=1):
            for label2 in neighbours[neighbours > label1]:
                label1label2_border = border(lab_img, label1, label2, Bc=connectivity,
                                             out=borders, always_return=False)
                border_min = np.min(int_img[label1label2_border])
                labels_max = np.min(
                    labels_maxima[np.array([label1 - 1, label2 - 1])])
                if (labels_max - border_min) < threshold:
                    to_merge.append((label1, label2))

        # check for convergence
        if len(to_merge) == 0:
            break

        # merge
        for ii in merge(to_merge):
            lab_img[np.isin(lab_img, list(ii))] = list(ii)[0]
#            lab_img_raveled[np.in1d(lab_img_raveled, list(ii))] = list(ii)[0]

#    lab_img = crop(slab_img, pad_width, copy=False)
    if lab_img.ndim == 3:
        lab_img = lab_img[1:-1, 1:-1, 1:-1]
    elif lab_img.ndim == 2:
        lab_img = lab_img[1:-1, 1:-1]
    if int_img.ndim == 3:
        int_img = int_img[1:-1, 1:-1, 1:-1]
    elif int_img.ndim == 2:
        int_img = int_img[1:-1, 1:-1]

#    int_img = crop(int_img, pad_width, copy=False)

    return lab_img
