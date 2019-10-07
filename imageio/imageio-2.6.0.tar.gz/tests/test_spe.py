import numpy as np
import pytest

import imageio
from imageio.plugins import spe
from imageio.testing import run_tests_if_main, get_test_dir, need_internet
from imageio.core import get_remote_file


test_dir = get_test_dir()


def test_spe_format():
    for name in ("spe", ".spe"):
        fmt = imageio.formats[name]
        assert isinstance(fmt, spe.SpeFormat)


def test_spe_reading():
    need_internet()
    fname = get_remote_file("images/test_000_.SPE")

    fr1 = np.zeros((32, 32), np.uint16)
    fr2 = np.ones_like(fr1)

    # Test imread
    im = imageio.imread(fname)
    ims = imageio.mimread(fname)

    np.testing.assert_equal(im, fr1)
    np.testing.assert_equal(ims, [fr1, fr2])

    # Test volread
    vol = imageio.volread(fname)
    vols = imageio.mvolread(fname)

    np.testing.assert_equal(vol, [fr1, fr2])
    np.testing.assert_equal(vols, [[fr1, fr2]])

    # Test get_reader
    r = imageio.get_reader(fname)

    np.testing.assert_equal(r.get_data(1), fr2)
    np.testing.assert_equal(list(r), [fr1, fr2])
    pytest.raises(IndexError, r.get_data, -1)
    pytest.raises(IndexError, r.get_data, 2)

    # check metadata
    md = r.get_meta_data()
    assert md["ROIs"] == [
        {"top_left": [238, 187], "bottom_right": [269, 218], "bin": [1, 1]}
    ]
    cmt = [
        "OD 1.0 in r, g                                                    "
        "              ",
        "000200000000000004800000000000000000000000000000000000000000000000"
        "0002000001000X",
        "                                                                  "
        "              ",
        "                                                                  "
        "              ",
        "ACCI2xSEQU-1---10000010001600300EA                              SW"
        "0218COMVER0500",
    ]
    assert md["comments"] == cmt
    np.testing.assert_equal(md["frame_shape"], fr1.shape)


run_tests_if_main()
