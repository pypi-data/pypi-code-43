import pyconrad.autoinit
import numpy as np
import os
import pytest

_ = pyconrad.ClassGetter()  # type: pyconrad.AutoCompleteConrad


def test_create_pointnd():

    _.PointND([2., 3.])
    _.PointND(np.array([2., 3.]))
    _.PointND(pyconrad.JArray(pyconrad.JDouble)([2., 3.]))
    _.PointND.from_list([2, 3])
    _.PointND.from_numpy(np.array([2, 3]))

    # These don't work:
    # _.PointND(np.array([2., 3.]).astype(np.float32))
    # _.PointND([2, 3])


def test_create_gridnd():

    _.Grid1D(10)
    _.Grid2D(10, 20)
    _.Grid3D(10, 20, 30)
    _.Grid4D(10, 20, 30, 50)


def test_gridnd__array__():

    np.array(_.Grid1D(10))
    np.array(_.Grid2D(10, 20))
    np.array(_.Grid3D(10, 20, 30))
    np.array(_.Grid4D(10, 20, 30, 50))


def test_numpy_to_grid1d():
    random_matrix = np.random.randn(10).astype(pyconrad.java_float_dtype)

    grid = _.Grid1D.from_numpy(random_matrix)

    converted = grid.as_numpy()

    assert np.allclose(converted, random_matrix)


def test_numpy_to_gridnd():

    for dim in range(2, 5):
        random_matrix = np.random.randn(
            *[(10 * (i + 1)) for i in range(dim)]).astype(pyconrad.java_float_dtype)

        if dim == 1:
            grid = _.Grid1D.from_numpy(random_matrix)
        elif dim == 2:
            grid = _.Grid2D.from_numpy(random_matrix)
        elif dim == 3:
            grid = _.Grid3D.from_numpy(random_matrix)
        elif dim == 4:
            grid = _.Grid4D.from_numpy(random_matrix)

        converted = grid.as_numpy()

        assert np.allclose(converted, random_matrix)

    for dim in range(2, 5):

        random_matrix = np.random.randn(
            *[(10 * (i + 1)) for i in range(dim)])

        if dim == 1:
            grid = _.Grid1D.from_numpy(random_matrix)
        elif dim == 2:
            grid = _.Grid2D.from_numpy(random_matrix)
        elif dim == 3:
            grid = _.Grid3D.from_numpy(random_matrix)
        elif dim == 4:
            grid = _.Grid4D.from_numpy(random_matrix)

        converted = grid.as_numpy()

        assert np.allclose(converted, random_matrix)


def test_numpy_to_numericgrid():

    for dim in range(2, 5):
        random_matrix = np.random.randn(
            *[(10 * (i + 1)) for i in range(dim)]).astype(pyconrad.java_float_dtype)

        grid = _.NumericGrid.from_numpy(random_matrix)
        converted = grid.as_numpy()

        assert np.allclose(converted, random_matrix)


@pytest.mark.skipif("CI" in os.environ and os.environ["CI"] == "true", reason="Skipping this test on Travis CI.")
def test_show_gridnd():

    for dim in range(2, 5):
        random_matrix = np.random.randn(
            *[(10 * (i + 1)) for i in range(dim)]).astype(pyconrad.java_float_dtype)

        if dim == 1:
            grid = _.Grid1D.from_numpy(random_matrix)
        elif dim == 2:
            grid = _.Grid2D.from_numpy(random_matrix)
        elif dim == 3:
            grid = _.Grid3D.from_numpy(random_matrix)
        elif dim == 4:
            grid = _.Grid4D.from_numpy(random_matrix)

        converted = grid.as_numpy()

        assert np.allclose(converted, random_matrix)


@pytest.mark.skipif("CI" in os.environ and os.environ["CI"] == "true", reason="Skipping this test on Travis CI.")
def test_show_numericgrid():
    for dim in range(2, 5):

        random_matrix = np.random.randn(
            *[(10 * (i + 1)) for i in range(dim)])

        grid = _.NumericGrid.from_numpy(random_matrix)
        converted = grid.as_numpy()

        assert np.allclose(converted, random_matrix)
        grid.show()
    pyconrad.ij().WindowManager.closeAllWindows()


@pytest.mark.skipif("CI" in os.environ and os.environ["CI"] == "true", reason="Skipping this test on Travis CI.")
def test_show_numericgrid_without_4D():
    for dim in range(2, 4):

        random_matrix = np.random.randn(
            *[(10 * (i + 1)) for i in range(dim)])

        grid = _.NumericGrid.from_numpy(random_matrix)
        converted = grid.as_numpy()

        assert np.allclose(converted, random_matrix)
        grid.show()
    pyconrad.ij().WindowManager.closeAllWindows()


def test_imageplus():

    b = pyconrad.ij().ImagePlus.from_numpy(np.array(_.Grid2D(10, 29)))
    c = pyconrad.ij().ImagePlus.from_numpy(np.array(_.Grid3D(10, 2, 4)))
    d = pyconrad.ij().ImagePlus.from_numpy(np.array(_.Grid4D(10, 32, 2, 2)))

    y = _.Grid2D(10, 29).as_imageplus()
    z = _.Grid3D(10, 2, 4).as_imageplus()
    w = _.Grid4D(10, 32, 2, 2).as_imageplus()

    assert y is not None
    assert z is not None
    assert w is not None

    b.as_grid()
    c.as_grid()
    d.as_grid()


@pytest.mark.skipif("CI" in os.environ and os.environ["CI"] == "true", reason="Skipping this test on Travis CI.")
def test_show_imageplus():
    for dim in range(2, 5):

        random_matrix = np.random.randn(
            *[(10 * (i + 1)) for i in range(dim)])

        if dim == 4:
            grid = pyconrad.edu().stanford.rsl.conrad.data.numeric.NumericGrid.from_numpy(random_matrix)
            ij = pyconrad.edu().stanford.rsl.conrad.utils.ImageUtil.wrapGrid4D(grid, "sas")
        else:
            ij = pyconrad.ij().ImagePlus.from_numpy(random_matrix)

        ij.show()
    pyconrad.ij().WindowManager.closeAllWindows()


if __name__ == "__main__":
    test_create_gridnd()
    test_create_pointnd()
    test_gridnd__array__()
    test_imageplus()
    test_numpy_to_grid1d()
    test_numpy_to_gridnd()
    test_numpy_to_numericgrid()
    test_show_gridnd()
    test_show_imageplus()
    test_show_numericgrid()
    test_show_numericgrid_without_4D()
