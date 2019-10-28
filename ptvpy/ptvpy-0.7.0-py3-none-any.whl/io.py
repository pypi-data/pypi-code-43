"""Tools to manage data on disk."""


import glob
import hashlib
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import imageio
import h5py

from . import __version__, PtvPyError
from .process import mean_frame
from .utils import LazyMapSequence, natural_sort_key


__all__ = ["NoParticleDataError", "Storage", "FrameLoader", "hash_files", "hash_arrays"]


class NoParticleDataError(PtvPyError):
    """No particle data where found in the storage file."""

    pass


class Storage(h5py.File):
    """Simple wrapper to handle IO for more complex types.

    This class extends its base class with the following functionality:

    - :meth:`save_df` and :meth:`load_df` allow round-tripping pandas.DataFrames.
    - Saves PtvPy's version string when creating or truncating a file. Otherwise it
      raises a warning if no or a mismatching version string was found.

    Parameters
    ----------
    name : str or path-like
        Path to the file which to open.
    mode : {"r", "r+", "w", "x", "a"}
        See :class:`h5py.File` for a list of supported file modes.
    args, kwargs :
        See :class:`h5py.File`.

    Notes
    -----
    Because the implementation was kept very simple, it is likely that storing
    DataFrames with more exotic or complex dtypes (especially "object") will
    fail. However numeric dtypes should work. While the DataFrame support is
    not as thorough as the one in panda's HDFStore, this class exposes the full
    range of h5py's API and allows attribute access and storage of more complex
    data. Furthermore 'pytables' can be skipped as a dependency.

    The way this wrapper stores DataFrames is by creating a new group at a
    desired `path`. This group then contains a dataset for each column in the
    DataFrame.

    .. _create_dataset:
       http://docs.h5py.org/en/stable/high/group.html#Group.create_dataset
    """

    def __init__(self, name, mode, **kwargs):
        super().__init__(name=name, mode=mode, **kwargs)

        version = f"PtvPy {__version__}"
        try:
            file_version = self.attrs["created_with"]
            if version != file_version:
                warnings.warn(
                    f"using storage file '{name}' that was created with a different "
                    f"version: current: '{version}', found: '{file_version}'",
                    stacklevel=2,
                )
        except KeyError:
            if len(self) == len(self.attrs) == 0:
                # Assume that file was newly created or truncated
                self.attrs["created_with"] = version
            else:
                warnings.warn(
                    f"couldn't find PtvPy version string in storage file '{name}'",
                    stacklevel=2,
                )

    def save_df(self, name, df, overwrite=False, **kwargs):
        """Store a pandas DataFrame.

        .. warning::

           - Doesn't preserve the index of a DataFrame. If you want to save the
             index convert it into a column beforehand.
           - Doesn't preserve column order.
           - Column names must be strings.
           - Saving DataFrames with non-numeric dtypes may fail.

        Parameters
        ----------
        name : str
            Name to store the DataFrame at. May be an absolute or relative path.
        df : pandas.DataFrame
            The DataFrame to store.
        overwrite : bool, optional
            If False, raises a TypeError if an object already exists at `name`.
            Otherwise an existing object is silently overwritten.
        kwargs : dict
            Additional keyword arguments used to create the dataset for each
            column in `df` (see create_dataset_).

        Returns
        -------
        group : h5py.Group
            The group containing the saved `df`.
        """
        if overwrite and name in self:
            del self[name]
        group = self.create_group(name)
        for name, series in df.items():
            group.create_dataset(name=name, data=series.values, **kwargs)
        return group

    def load_df(self, path):
        """Load a pandas DataFrame.

        Parameters
        ----------
        path : str
            The path to the stored DataFrame.

        Returns
        -------
        df : pandas.DataFrame
            The loaded DataFrame.
        """
        group = self[path]
        df = pd.DataFrame(
            {
                # Load actual content by appending [:], without it creation may be
                # super slow for large DataFrames
                name: group[name][:]
                for name in group.keys()
            }
        )
        return df

    def save_file(self, name, file, overwrite=False, **kwargs):
        """Store the content of a file as a binary blob inside the HDF file.

        Parameters
        ----------
        name : str
            Name to store the file at. May be an absolute or relative path.
        file : str or Path
            Path to the file to store.
        overwrite : bool, optional
            If False, raises a RuntimeError if an object already exists at `name`.
            Otherwise an existing object is silently overwritten.
        kwargs : dict
            Additional keyword arguments used to create the dataset (see
            create_dataset_).

        Returns
        -------
        dset : h5py.Dataset
            The dataset containing the raw content of the file.

        Notes
        -----
        Files stored this way may be extracted with h5dump_ by using the options
        "-b FILE", "-d" and "-o".

        .. _h5dump: https://support.hdfgroup.org/HDF5/doc/RM/Tools.html#Tools-Dump
        """
        if overwrite and name in self:
            del self[name]
        with open(file, "rb") as stream:
            content = stream.read()
        dset = self.create_dataset(name, data=np.void(content), **kwargs)
        return dset


class FrameLoader:
    """Helper to load frames without wasting memory and CPU time.

    Parameters
    ----------
    pattern : str
        The path using a glob pattern to match the image files.
    slice_ : slice, optional
        Select a subset of all frames found with `pattern`.

    Notes
    -----
    After calling the method `queue_background_removal` the background will
    be removed upon loading a frame. If the function was provided with a
    file path the background is cached as an intermediate result. If we provide
    the same path again on a new loader we can reuse the result under the
    condition that exactly the same frames are used again. This is checked by
    comparing a hash of the data files specified by `pattern`.

    Examples
    --------
    Most simple way to load TIFF files located inside a directory "data":

    >>> frames = FrameLoader("data/*.tiff").lazy_frame_sequence()

    Load frames but (optionally) remove background, only use first 100 frames
    and load background from "cache.hdf5" if it was already calculated:

    >>> loader = FrameLoader("data/*.tiff", slice(None, 100))
    >>> loader.remove_background("cache.hdf5")  # doctest: +SKIP
    >>> frames = loader.lazy_frame_sequence()
    """

    def __init__(self, pattern, slice_=None):
        self.pattern = str(pattern)  #: Same as input argument.
        self.slice_ = slice_  #: Same as input argument.
        #: Boolean flag that is true when the background was loaded from cache
        #: (bool or None).
        self.used_background_cache = None
        self._hash = None
        self._background = None
        self._load_func = imageio.imread

    @property
    def files(self):
        """
        Paths to the files the frames are loaded from (list[Path], read-only).
        They are sorted naturally [1]_ and not in alphabetical order.

        .. [1] https://en.wikipedia.org/wiki/Natural_sort_order
        """
        files = glob.glob(self.pattern)
        files = sorted(files, key=natural_sort_key)
        files = [Path(f) for f in files]
        if self.slice_ is not None:
            files = files[self.slice_]
        return files

    @property
    def hash(self):
        """
        Hexadecimal digits unique to the used data files (str, read-only).
        """
        if self._hash is None:
            self._hash = hash_files(self.files)
        return self._hash

    def lazy_frame_sequence(self):
        """Lazily load frames from the disk.

        Returns
        -------
        frames : LazyMapSequence[ndarray]
            A sequence of frames. Each frame is only loaded from disk when it
            is accessed directly.
        """
        return LazyMapSequence(self._load_func, self.files)

    def load_background(self, cache_path=None):
        """Load (calculate) the average per pixel for all used frames.

        Parameters
        ----------
        cache_path : str, optional
            Path to an HDF5 file that is used to cache the background. If not
            provided or a cache matching the used frames doesn't exist it is
            calculated.

        Returns
        -------
        background : ndarray
            An array matching the frames in shape containing the average per
            pixel for all used frames.
        """
        if self._background is None and cache_path is not None:
            self._background = self._load_background_cache(cache_path)
            self.used_background_cache = True

        if self._background is None:
            self._background = mean_frame(self.lazy_frame_sequence())
            self.used_background_cache = False

        if cache_path is not None and not self.used_background_cache:
            self._save_background_cache(cache_path, self._background)

        return self._background

    def remove_background(self, cache_path=None):
        """Automatically remove background when loading a frame.

        After calling this method all loaded frames returned will have their
        background removed.

        Parameters
        ----------
        cache_path : str, optional
            Path to an HDF5 file that is used to cache the background. If not
            provided or a cache matching the used frames doesn't exist it is
            calculated.
        """
        if self._background is None:
            self._background = self.load_background(cache_path)

        def func(path):
            frame = imageio.imread(path)
            frame = frame.astype(np.float64) - self._background
            frame[frame < 0] = 0
            return frame

        self._load_func = func

    def _load_background_cache(self, path):
        try:
            with h5py.File(path, "r") as file:
                if file["background"].attrs["hash"] == self.hash:
                    # Hash matches -> use cached result
                    return file["background"][...]
        except (OSError, KeyError):
            pass
        return None

    def _save_background_cache(self, path, background):
        with Storage(path, "a") as file:
            if "background" in file:
                del file["background"]
            # Cache the compressed result with the digest for next use
            file.create_dataset(
                "background", data=background, compression="gzip", compression_opts=8
            )
            file["background"].attrs["hash"] = self.hash
            file["background"].attrs[
                "description"
            ] = f"average per pixel for all images matching {ascii(self.pattern)}"


def hash_files(paths, *, algorithm=None, buffer_size=2 ** 20, hash_names=False):
    """Hash the given `files`.

    Parameters
    ----------
    paths : Iterator[path_like]
        Paths to the files to hash. The order doesn't matter because they are
        sorted before hashing.
    algorithm : _hashlib.HASH, optional
        An object implementing the interface of the algorithms in Python's
        module `hashlib`; namely the methods `update` and `hexdigest`. If not
        provided the algorithm defaults to `hashlib.sha1()`.
    buffer_size : int, optional
        The buffer size in bytes used when hashing files. Changing this
        shouldn't change the computed hash.
    hash_names : bool, optional
        Hash file names as well. The actual location (file path before the file)
        name is ignored.

    Returns
    -------
    hexdigest : str
        A digest as a string of hexadecimal digits.
    """
    if algorithm is None:
        algorithm = hashlib.sha1()
    for path in sorted(paths):
        if hash_names:
            algorithm.update(Path(path).name.encode())
        with open(path, "rb") as stream:
            while True:
                buffer = stream.read(buffer_size)
                if not buffer:
                    break
                algorithm.update(buffer)
    return algorithm.hexdigest()


def hash_arrays(arrays, *, algorithm=None):
    """Hash the content of arrays.

    Parameters
    ----------
    arrays : Iterable[bytes-like]
        A iterable of objects supporting Python's Buffer Protocol like
        `numpy.ndarray` or `memoryview`.
    algorithm : _hashlib.HASH, optional
        An object implementing the interface of the algorithms in Python's
        module `hashlib`; namely the methods `update` and `hexdigest`. If not
        provided the algorithm defaults to `hashlib.sha1()`.

    Returns
    -------
    hexdigest : str
        A digest as a string of hexadecimal digits.
    """
    if algorithm is None:
        algorithm = hashlib.sha1()
    for obj in arrays:
        algorithm.update(obj)
    return algorithm.hexdigest()
