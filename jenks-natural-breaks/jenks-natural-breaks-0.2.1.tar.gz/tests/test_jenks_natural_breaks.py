import os.path as osp

import numpy as np
from six.moves import zip_longest

from jenks_natural_breaks import classify


def fp_approx_equal(v1, v2):
    return abs(v1 - v2) < 10e-6


def assert_all_approx_equal(result, expected):
    assert all(fp_approx_equal(r, e) for r, e in zip_longest(result, expected)), (
        "result ({}) != expected ({})".format(result, expected))


def test_main():
    data = np.load(osp.join(osp.dirname(__file__), "test_data.npy"))
    expected = [
        0.00054219615880457539,
        0.207831589876042,
        0.42214371025157071,
        0.62704148582439201,
        0.81435907344112834,
        0.99956237607090714]
    assert_all_approx_equal(classify(data, 5), expected)

    # assigns correct breaks (small gaps between classes)
    assert_all_approx_equal(classify(np.array([1, 2, 4, 5, 7, 9, 10, 20]), 3), [1, 7, 20, 20])

    # assigns correct breaks (large gaps between classes)
    assert_all_approx_equal(classify(np.array([2, 32, 33, 34, 100]), 3), [2, 32, 100, 100])

    # assigns correct breaks (breaking N points into N classes)
    assert_all_approx_equal(classify(np.array([9, 10, 11, 12, 13]), 5), [9, 10, 11, 12, 13, 13])


if __name__ == "__main__":
    test_main()
