"""

"""

import os

import pytest

import pyconrad.autoinit  # NOQA


@pytest.mark.skipif("CI" in os.environ and os.environ["CI"] == "true", reason="No Conrad.xml on CI")
def test_get_projection_matrices():
    import pyconrad.config
    matrices = pyconrad.config.get_projection_matrices()
    for m in matrices:
        print(m)


def main():
    test_get_projection_matrices()


if __name__ == '__main__':
    main()
