import sys
from distutils.version import LooseVersion

from qai.meta import pypi_versions


if __name__ == "__main__":
    local_version = sys.argv[1]

    pypi_versions = pypi_versions.get_pypi_versions()
    print(f"found the following versions on pypi: {pypi_versions}")
    pypi_max_version = pypi_versions[-1]

    if LooseVersion(local_version) > LooseVersion(pypi_max_version):
        print(
            f"found local version {local_version} and highest version on PyPi {pypi_max_version}"
        )
        exit(0)
    else:
        print(
            "\nThe local VERSION is not greater than the largest already published version on PyPi!"
            " Please increment the VERSION before trying to release.\n"
        )
        exit(1)
