import warnings
import pyconrad
import time
import pyconrad
import os
import pytest
import numpy as np


@pytest.mark.skipif("CI" in os.environ and os.environ["CI"] == "true", reason="Skipping this test on Travis CI.")
def test_basic_example():
    import pyconrad_examples.first_steps._1_basic_example
    pyconrad.ij().WindowManager.closeAllWindows()
    return


@pytest.mark.skipif("CI" in os.environ and os.environ["CI"] == "true", reason="Skipping this test on Travis CI.")
def test_numpy_example():
    import pyconrad_examples.first_steps._3_numpy_and_conrad
    pyconrad.ij().WindowManager.closeAllWindows()
    return


@pytest.mark.skipif("CI" in os.environ and os.environ["CI"] == "true", reason="Skipping this test on Travis CI.")
def test_run_ij_commands():
    #import pyconrad_examples.first_steps._5_run_ij_commands
    pyconrad.ij().WindowManager.closeAllWindows()
    return


@pytest.mark.skipif("WITH_OPENCL" not in os.environ or os.environ["WITH_OPENCL"] == "0", reason="Skipping this test on Travis CI.")
def test_opencl_example():
    import pyconrad_examples.opencl
    pyconrad.ij().WindowManager.closeAllWindows()
    return


@pytest.mark.skipif("WITH_OPENCL" not in os.environ or os.environ["WITH_OPENCL"] == "0", reason="Skipping this test on Travis CI.")
def test_opencl_custom_kernel_example():
    import pyconrad_examples.opencl_custom_kernel
    pyconrad.ij().WindowManager.closeAllWindows()
    return


def test_readme_example():
    import pyconrad.autoinit

    _ = pyconrad.ClassGetter()

    # Create PyGrid from numpy array (more efficient if using Java float type pyconrad.java_float_dtype)
    array = np.random.rand(4, 2, 3).astype(pyconrad.java_float_dtype)
    grid = _.NumericGrid.from_numpy(array)

    # Manipulate data in using CONRAD at Position (x,y,z) = (0,1,3)
    grid.setValue(5.0, [0, 1, 3])

    # Get modified array
    new_array = grid.as_numpy()

    # Attention: Python has a different indexing (z,y,x)
    print('Old value: %f' % array[3, 1, 0])
    print('New value: %f' % new_array[3, 1, 0])


if __name__ == "__main__":
    # test_basic_example()
    test_numpy_example()
    test_readme_example()
    test_run_ij_commands()
