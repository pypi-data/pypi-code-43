"""Tests for the IO module of PtvPy."""


import hashlib
from pathlib import Path

import imageio
import pytest
import numpy as np
import pandas as pd
from numpy.testing import assert_allclose
from pandas.util.testing import assert_frame_equal

import ptvpy.io as ptvpy_io


def test_hash_files(fresh_project):
    """Basic tests for `hash_files` function."""
    files = list(Path(".").glob("**/*"))
    # Digest with default values
    digest = ptvpy_io.hash_files(files)

    # Buffer size shouldn't change digest
    assert digest == ptvpy_io.hash_files(files, buffer_size=2 ** 12)
    assert digest == ptvpy_io.hash_files(files, buffer_size=2 ** 18)

    # Order shouldn't matter
    assert digest == ptvpy_io.hash_files(files[::-1])

    # Skipping one file should matter
    assert digest != ptvpy_io.hash_files(files[:-1])
    # Different algorithms should yield different digests
    assert digest != ptvpy_io.hash_files(files, algorithm=hashlib.md5())
    assert digest != ptvpy_io.hash_files(files, algorithm=hashlib.blake2b())

    digest_names = ptvpy_io.hash_files(files, hash_names=True)
    # Hashing with file names included should yield different digest
    assert digest != digest_names
    # Renaming a file should change the digest
    # (rename only returns new Path since Python 3.8.)
    files[0].rename("new_name")
    files[0] = files[0].parent / "new_name"
    assert digest_names != ptvpy_io.hash_files(files, hash_names=True)


# TODO test LazyLoadingSequence (slicing)


def _particles_dummy():
    """Create DataFrame like the one created during processing."""
    return pd.DataFrame(
        {
            "particles": np.arange(0, 50, dtype=np.int64),
            "frames": np.arange(50, 100, dtype=np.int64),
            "x": np.linspace(0, 1, 50),
            "y": np.linspace(0, 2, 50),
            "mass": np.linspace(0, 3, 50),
            "size": np.linspace(0, 4, 50),
            "signal": np.linspace(0, 5, 50),
            "raw_mass": np.linspace(0, 6, 50),
            "ep": np.linspace(0, 7, 50),
            "dx": np.linspace(0, 8, 50),
            "dy": np.linspace(0, 9, 50),
            "v": np.linspace(0, 10, 50),
        }
    )


@pytest.mark.parametrize(
    "df",
    [
        # dtype is homogeneous
        pd.DataFrame(np.arange(90).reshape(30, 3), columns=["a", "b", "c"]),
        # dtype of columns differs
        pd.DataFrame({"x": np.arange(30), "y": np.linspace(0, 1, 30)}),
        # DataFrame as it is actually used by PtvPy
        _particles_dummy(),
    ],
)
def test_Storage(tmp_path, df):
    """Basic round-tripping test for simple DataFrames."""
    file_path = tmp_path / "test.h5"
    with ptvpy_io.Storage(file_path, "x") as file:
        # Save subset of DataFrame that would fail in later comparison
        # (overwritten further down)
        file.save_df("df", df.iloc[:1, :])
    with ptvpy_io.Storage(file_path, "r+") as file:
        match = r"Unable to create group \(name already exists\)"
        with pytest.raises(ValueError, match=match):
            file.save_df("df", df)
        # With overwrite=True (default) saving should be successful
        file.save_df("df", df, overwrite=True)
    with ptvpy_io.Storage(file_path, "r+") as file:
        # Save in nested hierarchy
        file.save_df("path/to/df2", df)

    with ptvpy_io.Storage(file_path, "r") as file:
        df_from_file = file.load_df("df")
        df2_from_file = file.load_df("path/to/df2")
    assert_frame_equal(df, df_from_file, check_exact=True, check_like=True)
    assert_frame_equal(df, df2_from_file, check_exact=True, check_like=True)


class Test_FrameLoader:
    def test_basic(self, fresh_project):
        loader = ptvpy_io.FrameLoader("*.tiff")
        assert len(loader.files) == 20
        assert loader.used_background_cache is None
        assert loader._load_func is imageio.imread
        frames = loader.lazy_frame_sequence()
        assert isinstance(frames, ptvpy_io.LazyMapSequence)

    def test_hash(self, fresh_project):
        hash_full = ptvpy_io.FrameLoader("*.tiff").hash
        hash_subset = ptvpy_io.FrameLoader("*.tiff", slice(1, None)).hash
        assert hash_full != hash_subset

    def test_background(self, fresh_project):
        raw_frames = ptvpy_io.FrameLoader("*.tiff").lazy_frame_sequence()
        desired = np.sum(raw_frames, axis=0) / len(raw_frames)

        loader = ptvpy_io.FrameLoader("*.tiff")
        background = loader.load_background()
        assert_allclose(background, desired)
        assert loader.used_background_cache is False
        loader.load_background("cache.hdf5")
        assert loader.used_background_cache is False
        assert Path("cache.hdf5").is_file()
        cache_hash = ptvpy_io.hash_files(["cache.hdf5"])

        # Create new loader to test if cache is reused
        loader = ptvpy_io.FrameLoader("*.tiff")
        background = loader.load_background("cache.hdf5")
        assert cache_hash == ptvpy_io.hash_files(["cache.hdf5"])
        assert loader.used_background_cache is True
        # Check content of returned array
        assert background.shape == raw_frames[0].shape
        assert_allclose(background, desired)

        # Cache shouldn't be reused if we the input is different
        loader = ptvpy_io.FrameLoader("*.tiff", slice(1, None))
        loader.load_background("cache.hdf5")
        assert loader.used_background_cache is False
        # Cache file should have changed
        assert cache_hash != ptvpy_io.hash_files(["cache.hdf5"])

    def test_queue_background_removal(self, fresh_project):
        loader = ptvpy_io.FrameLoader("*.tiff")
        raw_frames = loader.lazy_frame_sequence()

        inital_load_function = loader._load_func
        loader.remove_background()
        # Loading function should have been patched
        assert inital_load_function is not loader._load_func

        cleaned_frames = loader.lazy_frame_sequence()
        for raw, cleaned in zip(raw_frames, cleaned_frames):
            assert np.any(np.not_equal(raw, cleaned))

    def test_natural_file_order(self, tmp_path):
        """Check that files are sorted naturally and not alphabetically."""
        files = [tmp_path / f"image_{i}.tiff" for i in range(8, 12)]
        for file in files:
            with open(file, "x"):
                pass
        loader = ptvpy_io.FrameLoader(tmp_path / "image_*.tiff")
        assert loader.files == files
