import pyconrad.autoinit
import numpy as np
import ij
import pytest
import os


@pytest.mark.skipif("CI" in os.environ and os.environ["CI"] == "true", reason="Skipping this test on Travis CI.")
def test_imshow():
    a = np.random.rand(20, 30)
    luts = ['Fire', 'Spectrum', 'Ice', 'Cyan']

    for lut in luts:
        pyconrad.imshow(a, lut=lut)

    ij.WindowManager.closeAllWindows()

    actions = ['FFT']

    for action in actions:
        pyconrad.imshow(a, run=action, lut='Fire')

    ij.WindowManager.closeAllWindows()

    actions = ['FFT']

    for action in actions:
        pyconrad.imshow(a, "foo", run=action, lut='Fire')


def main():
    test_imshow()


if __name__ == '__main__':
    main()
