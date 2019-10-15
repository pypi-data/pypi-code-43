#!/usr/bin/env python
#
# imagecache.py - A cache for NIFTI images
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provide the :class:`ImageCache` class, a simple in-memory
cache for nibabel-loaded files.
"""


import            collections
import            logging
import os.path as op

import numpy   as np
import nibabel as nib


log = logging.getLogger(__name__)


def size(img):
    """Return the size of the given ``nibabel`` NIfTI image in megabytes.

    The returned size only takes into account the image data, not its header.

    Only spatial images (e.g. NIfTI) are considered; all other file types
    are assumed to take up one megabyte.
    """

    if not isinstance(img, nib.AnalyzeImage):
        return 1

    dtype = img.get_data_dtype()
    kb    = np.prod(img.shape) * dtype.itemsize
    return kb / 1048576.0


class ImageCache(object):
    """The ``ImageCache`` is just a cache for loading ``nibabel`` images (and
    other data types).  Its purpose is to avoid re-loading the same image
    multiple times - once an image has been loaded through the cache, it will
    be kept in the cache for subsequent access.

    An image can be loaded by accessing the ``ImageCache`` as a ``dict``::

        cache = ImageCache()

        # the image is loaded on first access
        img = cache['myimage.nii.gz']

        # on subsequent accesses, the image
        # is returned from the cache
        img = cache['myimage.nii.gz']
    """

    def __init__(self, maxsize=32768):
        """Create the cache.

        :arg maxsize: Maximum size of the cache in megabytes. When the cache
                      reaches this size, old entries are dropped.
        """
        self.__images      = collections.OrderedDict()
        self.__imagesizes  = {}
        self.__currentsize = 0
        self.__maxsize     = maxsize

        log.debug('Initialising ImageCache(maxsize=%iGB)', maxsize / 1024)


    def __getitem__(self, imagefile):
        """Return the ``nibabel`` image corresponding to the given
        ``imagefile``, loading it if necessary.
        """

        imagefile = op.realpath(op.abspath(imagefile))
        image     = self.__images.get(imagefile, None)

        if image is not None:

            # keep the images dict
            # ordered by access time
            log.debug('Touching %s', imagefile)
            self.__images.move_to_end(imagefile)
            return image

        image           = nib.load(imagefile)
        self[imagefile] = image
        return image


    def __setitem__(self, imagefile, image):
        """Add something to the cache. This is intended to be used for
        storing derived, in-memory-only images.
        """

        # imagefile may not be a valid
        # file system path, but we transform
        # it in this way because all keys
        # passed to __getitem__ get
        # transformed in the same way.

        imagefile                    = op.realpath(op.abspath(imagefile))
        imagesize                    = size(image)
        self.__images[    imagefile] = image
        self.__imagesizes[imagefile] = imagesize

        newsize = self.__currentsize + imagesize

        log.debug('Adding %s (%0.2f / %0.0f)',
                  imagefile, newsize, self.__maxsize)

        while newsize > self.__maxsize:
            lrufile  = self.__images    .popitem(last=False)[0]
            lrusize  = self.__imagesizes.pop(    lrufile)

            log.debug('Removing %s (%0.2f)', lrufile, lrusize)

            newsize -= lrusize

        self.__currentsize = newsize
